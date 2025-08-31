# src/feedforge/core.py
from googleapiclient.discovery import build
import asyncio
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import openai
from typing import List
from dotenv import load_dotenv
from pathlib import Path
import httpx

class YouTubeFeedCustomizer:
    def __init__(self, analysis_base_url: str = "http://127.0.0.1:8000"):
        self._load_env()
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.youtube_key = os.getenv('YOUTUBE_API_KEY')

        # Check if API keys are set
        if not self.openai_key:
            raise ValueError(
                "OpenAI API key not provided. Either:\n"
                "1. Set OPENAI_API_KEY environment variable\n"
                "2. Pass openai_key parameter to YouTubeFeedCustomizer\n"
                "3. Create a .env file with OPENAI_API_KEY"
            )
        if not self.youtube_key:
            raise ValueError(
                "YouTube API key not provided. Either:\n"
                "1. Set YOUTUBE_API_KEY environment variable\n"
                "2. Pass youtube_key parameter to YouTubeFeedCustomizer\n"
                "3. Create a .env file with YOUTUBE_API_KEY"
            )

        # self.llm = OpenAILLM(model='gpt-4o', api_key=self.openai_key)
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_key)
        # self.browser = Browser(
        #     config=BrowserConfig(
        #         chrome_instance_path=self._get_chrome_path(),
        #         headless=False,
        #     )
        # )
        self.analysis_base_url = analysis_base_url.rstrip('/')
        self.selenium_driver = None
        self.headless = False

    def _get_chrome_path(self):
        if os.name == 'nt':  # Windows
            return r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        elif os.name == 'posix':  # macOS and Linux
            if os.path.exists('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'):
                return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            return '/usr/bin/google-chrome'
        raise OSError("Unsupported operating system")

    def _get_firefox_path(self):
        if os.name == 'nt':  # Windows
            return r'C:\Program Files\Mozilla Firefox\firefox.exe'
        elif os.name == 'posix':  # macOS and Linux
            if os.path.exists('/Applications/Firefox.app/Contents/MacOS/firefox'):
                return '/Applications/Firefox.app/Contents/MacOS/firefox'
            return '/usr/bin/firefox'
        raise OSError("Unsupported operating system")

    def _init_firefox_driver(self):
        """Initialize Firefox WebDriver with Selenium."""
        import geckodriver_autoinstaller
        import configparser

        # Auto-install geckodriver if not found
        geckodriver_autoinstaller.install()

        firefox_options = FirefoxOptions()
        if self.headless:
            firefox_options.add_argument('--headless')

        # Try to find and use existing Firefox profile from profiles.ini
        try:
            firefox_base_dir = os.path.expanduser("~/Library/Application Support/Firefox")
            profiles_ini_path = os.path.join(firefox_base_dir, "profiles.ini")

            if os.path.exists(profiles_ini_path):
                # Parse profiles.ini to find the default profile
                config = configparser.ConfigParser()
                config.read(profiles_ini_path)

                # Look for the default profile
                default_profile_path = None
                for section in config.sections():
                    if section.startswith('Profile') and config.has_option(section, 'Default') and config.get(section, 'Default') == '1':
                        if config.has_option(section, 'Path'):
                            relative_path = config.get(section, 'Path')
                            if config.has_option(section, 'IsRelative') and config.get(section, 'IsRelative') == '1':
                                default_profile_path = os.path.join(firefox_base_dir, relative_path)
                            else:
                                default_profile_path = relative_path
                            break

                # If no profile marked as Default=1, look for any install-specific default
                if not default_profile_path:
                    for section in config.sections():
                        if section.startswith('Install') and config.has_option(section, 'Default'):
                            relative_path = config.get(section, 'Default')
                            default_profile_path = os.path.join(firefox_base_dir, relative_path)
                            break

                if default_profile_path and os.path.exists(default_profile_path):
                    print(f"🦊 Using Firefox profile: {os.path.basename(default_profile_path)}")
                    firefox_options.add_argument(f"--profile")
                    firefox_options.add_argument(default_profile_path)
                else:
                    print("🦊 No default Firefox profile found, using new profile")
            else:
                print("🦊 No profiles.ini found, using new Firefox profile")

            self.selenium_driver = webdriver.Firefox(options=firefox_options)
            print(f"🦊 Firefox browser launched successfully!")
        except Exception as e:
            print(f"Error launching Firefox: {e}")
            raise

    def _init_chrome_driver(self):
        """Initialize Chrome WebDriver with Selenium."""
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        import chromedriver_autoinstaller

        # Auto-install chromedriver if not found
        chromedriver_autoinstaller.install()

        chrome_options = ChromeOptions()
        if self.headless:
            chrome_options.add_argument('--headless')

        # Use a clean FeedForge-specific profile to avoid conflicts
        feedforge_chrome_profile = os.path.expanduser("~/.feedforge_chrome_profile")
        chrome_options.add_argument(f"--user-data-dir={feedforge_chrome_profile}")

        # Additional Chrome options for better automation
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        try:
            self.selenium_driver = webdriver.Chrome(options=chrome_options)
            self.selenium_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print(f"🌐 Chrome browser launched successfully!")
        except Exception as e:
            print(f"Error launching Chrome: {e}")
            raise

    async def _automate_firefox_videos(self, video_urls, duration):
        """Automate video playback for Firefox using Selenium."""
        if not self.selenium_driver:
            self._init_firefox_driver()

        try:
            for i, video_url in enumerate(video_urls, 1):
                print(f"🎬 Opening video {i}/{len(video_urls)}: {video_url}")

                # Navigate to video
                self.selenium_driver.get(video_url)

                # Wait for page to load
                time.sleep(3)

                # Try to click the play button to start the video
                try:
                    # Wait for play button to be clickable and click it
                    play_button = WebDriverWait(self.selenium_driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label*="Play"], .ytp-play-button, .ytp-large-play-button'))
                    )
                    play_button.click()
                    print(f"▶️  Started playing video {i}")
                except Exception as e:
                    # If play button not found, try clicking on the video player itself
                    try:
                        video_player = WebDriverWait(self.selenium_driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, '.html5-video-player, #movie_player'))
                        )
                        video_player.click()
                        print(f"▶️  Started playing video {i} (clicked player)")
                    except Exception as e2:
                        print(f"⚠️  Could not start video {i}: {e2}")

                # Wait for specified duration while video plays
                print(f"⏱️  Playing video {i} for {duration} seconds...")
                time.sleep(duration)

        except Exception as e:
            print(f"Error during Firefox automation: {e}")
        finally:
            if self.selenium_driver:
                self.selenium_driver.quit()
                print("🦊 Firefox browser closed")

    async def _automate_chrome_videos(self, video_urls, duration):
        """Automate video playback for Chrome using Selenium."""
        if not self.selenium_driver:
            self._init_chrome_driver()

        try:
            for i, video_url in enumerate(video_urls, 1):
                print(f"🎬 Opening video {i}/{len(video_urls)}: {video_url}")

                # Navigate to video
                self.selenium_driver.get(video_url)

                # Wait for page to load
                time.sleep(3)

                # Try to click the play button to start the video
                try:
                    # Wait for play button to be clickable and click it
                    play_button = WebDriverWait(self.selenium_driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label*="Play"], .ytp-play-button, .ytp-large-play-button'))
                    )
                    play_button.click()
                    print(f"▶️  Started playing video {i}")
                except Exception as e:
                    # If play button not found, try clicking on the video player itself
                    try:
                        video_player = WebDriverWait(self.selenium_driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, '.html5-video-player, #movie_player'))
                        )
                        video_player.click()
                        print(f"▶️  Started playing video {i} (clicked player)")
                    except Exception as e2:
                        print(f"⚠️  Could not start video {i}: {e2}")

                # Wait for specified duration while video plays
                print(f"⏱️  Playing video {i} for {duration} seconds...")
                time.sleep(duration)

        except Exception as e:
            print(f"Error during Chrome automation: {e}")
        finally:
            if self.selenium_driver:
                self.selenium_driver.quit()
                print("🌐 Chrome browser closed")

    def _load_env(self):
        """Try to load .env file from current directory or parent directories."""
        current_dir = Path.cwd()

        # Check current directory and up to 3 parent directories
        for _ in range(4):
            env_path = current_dir / '.env'
            if env_path.exists():
                load_dotenv(env_path)
                return
            if current_dir.parent == current_dir:
                break
            current_dir = current_dir.parent

        # Also check user's home directory
        home_env = Path.home() / '.feedforge.env'
        if home_env.exists():
            load_dotenv(home_env)

    async def _call_analysis_service(self, user_input: str, max_results_per_keyword: int = 2, num_keywords: int = 5):
        url = f"{self.analysis_base_url}/analyze"
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json={
                "description": user_input,
                "max_results_per_keyword": max_results_per_keyword,
                "num_keywords": num_keywords,
            })
            resp.raise_for_status()
            data = resp.json()
            keywords = data.get('keywords', [])
            videos = data.get('videos', [])
            return keywords, videos

    async def customize_feed(self, user_input, num_videos=10, duration=2, browser='firefox'):
        """Customize YouTube feed by calling analysis microservice and using browser automation."""
        try:
            print("🔍 Contacting analysis service...")
            keywords, videos = await self._call_analysis_service(user_input, num_keywords=5)
            print(f"✅ Generated topics: {', '.join(keywords)}")

            if not videos:
                print("❌ No videos found!")
                return

            videos = videos[:num_videos] if num_videos else videos
            print(f"\n🎬 Found {len(videos)} videos for playback")

            # Use Firefox for browser automation
            if browser.lower() == 'firefox':
                print("\n🦊 Starting Firefox browser automation...")
                await self._automate_firefox_videos(videos, duration)
            else:
                print("\n🌐 Starting Chrome browser automation...")
                await self._automate_chrome_videos(videos, duration)

            print("\n✨ Feed customization complete!")

        except Exception as e:
            print(f"❌ Error during feed customization: {e}")
            # Clean up resources
            if hasattr(self, 'selenium_driver') and self.selenium_driver:
                self.selenium_driver.quit()
