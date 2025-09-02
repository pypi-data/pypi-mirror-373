# src/feedforge/core.py
import asyncio
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
import time
from typing import List, Optional, Tuple
from dotenv import load_dotenv
import httpx
import json

class YouTubeFeedCustomizer:
    def __init__(self, analysis_base_url: str = "http://127.0.0.1:8000"):
        # Since we're using a backend service, we don't need API keys locally
        self.analysis_base_url = analysis_base_url.rstrip('/')
        self.selenium_driver = None
        self.headless = False
        self.chrome_session_file = os.path.expanduser("~/.feedforge_chrome_session.json")

        # Load environment just in case for local development
        self._load_env()

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
            # Determine Firefox profile directory based on OS
            if os.name == 'nt':  # Windows
                firefox_base_dir = os.path.expanduser(r'~\AppData\Roaming\Mozilla\Firefox')
            elif os.name == 'posix':  # macOS and Linux
                if os.path.exists(os.path.expanduser('~/Library/Application Support/Firefox')):
                    # macOS
                    firefox_base_dir = os.path.expanduser('~/Library/Application Support/Firefox')
                else:
                    # Linux
                    firefox_base_dir = os.path.expanduser('~/.mozilla/firefox')

            profiles_ini_path = os.path.join(firefox_base_dir, 'profiles.ini')

            if os.path.exists(profiles_ini_path):
                print(f"🦊 Found Firefox profiles at: {firefox_base_dir}")
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
                print(f"🦊 No profiles.ini found at {profiles_ini_path}, using new Firefox profile")

            self.selenium_driver = webdriver.Firefox(options=firefox_options)
            print(f"🦊 Firefox browser launched successfully!")
        except Exception as e:
            print(f"Error launching Firefox: {e}")
            raise

    def _attach_to_chrome_session(self, executor_url: str, session_id: str):
        """Attach to an existing Chrome session using the Stack Overflow solution."""
        original_execute = WebDriver.execute

        def new_command_execute(self, command, params=None):
            if command == "newSession":
                # Mock the response
                return {'success': 0, 'value': None, 'sessionId': session_id}
            else:
                return original_execute(self, command, params)

        # Patch the function before creating the driver object
        WebDriver.execute = new_command_execute
        driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
        driver.session_id = session_id
        # Replace the patched function with original function
        WebDriver.execute = original_execute
        return driver

    def _save_chrome_session(self, driver):
        """Save Chrome session info to a file."""
        try:
            # Try to get the executor URL - different methods for different Selenium versions
            executor_url = None
            if hasattr(driver.command_executor, '_url'):
                executor_url = driver.command_executor._url
            elif hasattr(driver.command_executor, 'get_remote_connection_headers'):
                # For newer Selenium versions, construct the URL
                executor_url = f"http://127.0.0.1:9222"
            else:
                # Default fallback
                executor_url = "http://127.0.0.1:9222"

            session_info = {
                'executor_url': executor_url,
                'session_id': driver.session_id
            }
            with open(self.chrome_session_file, 'w') as f:
                json.dump(session_info, f)
            print(f"💾 Chrome session saved to {self.chrome_session_file}")
        except Exception as e:
            print(f"⚠️  Could not save Chrome session: {e}")

    def _load_chrome_session(self) -> Optional[Tuple[str, str]]:
        """Load Chrome session info from file if it exists."""
        if os.path.exists(self.chrome_session_file):
            try:
                with open(self.chrome_session_file, 'r') as f:
                    session_info = json.load(f)
                return session_info['executor_url'], session_info['session_id']
            except Exception as e:
                print(f"⚠️  Error loading Chrome session: {e}")
        return None

    def _init_chrome_driver(self):
        """Initialize Chrome WebDriver - either attach to existing session or create new one."""
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        import chromedriver_autoinstaller

        # Auto-install chromedriver if not found
        chromedriver_autoinstaller.install()

        # Skip session attachment on Windows due to compatibility issues
        if os.name != 'nt':  # Only try session attachment on non-Windows systems
            # First, try to attach to an existing Chrome session
            session_info = self._load_chrome_session()
            if session_info:
                executor_url, session_id = session_info
                try:
                    print(f"🔗 Attempting to attach to existing Chrome session...")
                    print(f"   Executor URL: {executor_url}")
                    print(f"   Session ID: {session_id}")

                    self.selenium_driver = self._attach_to_chrome_session(executor_url, session_id)

                    # Test if the session is still valid
                    self.selenium_driver.current_url
                    print(f"✅ Successfully attached to existing Chrome session!")
                    return
                except Exception as e:
                    print(f"⚠️  Could not attach to existing session: {e}")
                    print("🌐 Starting new Chrome instance...")

        # If attachment failed or no session info, start a new Chrome instance
        chrome_options = ChromeOptions()
        if self.headless:
            chrome_options.add_argument('--headless')

        # Determine Chrome user data directory based on OS
        if os.name == 'nt':  # Windows
            chrome_user_data = os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data')
            # Windows requires a separate profile for automation with remote debugging
            feedforge_chrome_profile = os.path.expanduser("~/.feedforge_chrome_profile")
            use_custom_profile = True
        elif os.name == 'posix':  # macOS and Linux
            if os.path.exists(os.path.expanduser('~/Library/Application Support/Google/Chrome')):
                # macOS
                chrome_user_data = os.path.expanduser('~/Library/Application Support/Google/Chrome')
            else:
                # Linux
                chrome_user_data = os.path.expanduser('~/.config/google-chrome')
            feedforge_chrome_profile = os.path.expanduser("~/.feedforge_chrome_profile")
            use_custom_profile = False

        # Set up Chrome profile
        try:
            if os.name == 'nt' or not os.path.exists(chrome_user_data):
                # On Windows or if default profile not found, use custom profile
                print(f"🌐 Using FeedForge Chrome profile at: {feedforge_chrome_profile}")
                chrome_options.add_argument(f"--user-data-dir={feedforge_chrome_profile}")
                if os.name == 'nt':
                    print("🌐 Note: Windows requires a separate profile for automation")
                    print("🌐 You may need to log in to YouTube on first run")
            else:
                # On macOS/Linux, use the default Chrome profile
                print(f"🌐 Using existing Chrome profile from: {chrome_user_data}")
                chrome_options.add_argument(f"--user-data-dir={chrome_user_data}")
                print("🌐 Using default Chrome profile (logged in)")
        except Exception as e:
            print(f"⚠️  Error setting Chrome profile: {e}")
            chrome_options.add_argument(f"--user-data-dir={feedforge_chrome_profile}")

        # Additional Chrome options for better automation
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Add remote debugging port for session attachment (non-Windows only)
        if os.name != 'nt':
            chrome_options.add_argument('--remote-debugging-port=9222')

        # Windows specific fixes
        if os.name == 'nt':
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-gpu-sandbox')
            chrome_options.add_argument('--no-first-run')
            chrome_options.add_argument('--no-default-browser-check')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--disable-gpu-driver-bug-workarounds')
            chrome_options.add_argument('--log-level=3')  # Suppress verbose logging
            chrome_options.add_argument('--silent')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        else:
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # Add option to keep browser open after script ends
        chrome_options.add_experimental_option("detach", True)

        try:
            self.selenium_driver = webdriver.Chrome(options=chrome_options)
            self.selenium_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Save session info for future use (non-Windows only)
            if os.name != 'nt':
                self._save_chrome_session(self.selenium_driver)
                print(f"💡 Tip: Keep this Chrome instance open to reuse it in future runs!")

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
            if os.name == 'nt':
                # On Windows, close the browser to avoid issues
                if self.selenium_driver:
                    self.selenium_driver.quit()
                    print("🌐 Chrome browser closed")
            else:
                # On non-Windows, keep it open for reuse
                print("🌐 Chrome browser kept open for future use")
                print("💡 To close it manually, use: customizer.close_chrome_session()")

    def close_chrome_session(self):
        """Manually close Chrome session and clean up session file."""
        if self.selenium_driver:
            try:
                self.selenium_driver.quit()
                print("🌐 Chrome browser closed")
            except Exception as e:
                print(f"⚠️  Error closing Chrome: {e}")

        # Remove session file
        if os.path.exists(self.chrome_session_file):
            try:
                os.remove(self.chrome_session_file)
                print("🗑️  Chrome session file removed")
            except Exception as e:
                print(f"⚠️  Error removing session file: {e}")

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
            # Clean up resources - only quit Firefox, keep Chrome open
            if hasattr(self, 'selenium_driver') and self.selenium_driver and browser.lower() == 'firefox':
                self.selenium_driver.quit()
