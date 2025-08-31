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

class OpenAILLM:
    """OpenAI LLM wrapper for generating keywords."""

    def __init__(self, model: str = "gpt-4o", api_key: str = None):
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=api_key)

    async def generate_keywords(self, prompt: str) -> str:
        """Generate keywords using OpenAI."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            return ""

class YouTubeFeedCustomizer:
    def __init__(self, browser='chrome', headless=True):
        self.browser_type = browser
        self.headless = headless

        # Get API keys from environment variables
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.youtube_key = os.getenv("YOUTUBE_API_KEY")

        # Check if API keys are set
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        if not self.youtube_key:
            raise ValueError("YOUTUBE_API_KEY environment variable not set")

        self.llm = OpenAILLM(model='gpt-4o', api_key=self.openai_key)
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_key)

        # Configure browser - both Firefox and Chrome use Selenium
        self.browser = None  # No longer using browser-use
        self.selenium_driver = None  # Will be initialized when needed

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

    async def _generate_keywords(self, user_input):
        """Generate relevant keywords from user input using OpenAI."""
        prompt = f"""
        Based on this description of video interests: "{user_input}"
        Generate 5 specific YouTube search keywords or phrases that would find relevant content.
        Return only the keywords, separated by commas. Make them specific and targeted.
        """

        response = await self.llm.generate_keywords(prompt)

        # The response is now a string directly from our OpenAI wrapper
        content = response.strip()
        keywords = [kw.strip() for kw in content.split(',') if kw.strip()]
        print(f"Generated topics: {', '.join(keywords)}")
        return keywords

    async def _search_videos(self, keywords, max_results_per_keyword=2):
        """Search videos for multiple keywords in parallel. Each keyword will fetch up to 10 videos."""
        def search_for_keyword(keyword):
            """Synchronous function to search YouTube."""
            try:
                print(f"\nSearching for keyword: {keyword}")
                request = self.youtube.search().list(
                    part="id",
                    q=keyword,
                    type="video",
                    maxResults=max_results_per_keyword,
                    videoDefinition="high",
                    relevanceLanguage="en"
                )
                response = request.execute()
                videos = [
                    f"https://www.youtube.com/watch?v={item['id']['videoId']}&mute=1"
                    for item in response['items']
                ]
                print(f"Found {len(videos)} videos for keyword: {keyword}")
                return {'keyword': keyword, 'videos': videos}
            except Exception as e:
                print(f"Error searching for keyword '{keyword}': {e}")
                return {'keyword': keyword, 'videos': []}

        # Run all searches in parallel using asyncio.to_thread
        tasks = [asyncio.to_thread(search_for_keyword, keyword) for keyword in keywords]
        results = await asyncio.gather(*tasks)

        # Group videos by keyword
        keyword_videos = {result['keyword']: result['videos'] for result in results}

        # Initialize variables for round-robin selection
        all_videos = []
        seen = set()
        keyword_indices = {keyword: 0 for keyword in keywords}
        active_keywords = set(keywords)

        # Keep selecting videos until we've exhausted all options
        while active_keywords:
            # Remove keywords that have no more videos
            active_keywords = {k for k in active_keywords
                             if keyword_indices[k] < len(keyword_videos[k])}

            if not active_keywords:
                break

            # Randomly select a keyword and get next video
            import random
            keyword = random.choice(list(active_keywords))
            video_index = keyword_indices[keyword]

            if video_index < len(keyword_videos[keyword]):
                video = keyword_videos[keyword][video_index]
                if video not in seen:
                    seen.add(video)
                    all_videos.append(video)
                keyword_indices[keyword] += 1

        print(f"\nTotal unique videos found: {len(all_videos)}")
        return all_videos

    async def customize_feed(self, user_input, num_videos=10, duration=5, browser="firefox"):
        """Customize YouTube feed using OpenAI for keywords and YouTube API for videos."""
        try:
            print("Generating relevant topics...")
            keywords = await self._generate_keywords(user_input)
            print(f"Generated topics: {', '.join(keywords)}")

            print("\nFinding relevant videos...")
            videos = await self._search_videos(keywords)
            print(videos)

            if not videos:
                print("No videos found!")
                return

            # Take only the requested number of videos
            videos = videos[:num_videos]
            print(f"\nUsing {len(videos)} videos for playback...")

            if browser == 'firefox':
                # Use Selenium for Firefox
                await self._automate_firefox_videos(videos, duration)
            else:
                # Use Selenium for Chrome
                await self._automate_chrome_videos(videos, duration)

            print("\nFeed customization complete!")

        except Exception as e:
            print(f"Error during feed customization: {e}")
            # Clean up resources
            if self.selenium_driver:
                self.selenium_driver.quit()
