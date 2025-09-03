"""
Simple Selenium driver
"""

import time
from typing import Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base import BaseDriver


class SeleniumDriver(BaseDriver):
    """
    Simple Selenium driver
    """

    def __init__(self, **kwargs):
        """
        Initialize the Selenium driver

        Args:
            **kwargs: Specific Selenium configurations
        """
        super().__init__(**kwargs)
        self.driver = None
        self.wait = None

    def setup(self, session_data: Dict, token: str, extension_id: str):
        """
        Configure the Selenium driver

        Args:
            session_data: Session data
            token: Authentication token
            extension_id: Extension ID
        """
        print("Configuring simple Selenium driver...")

        # Configure Chrome Options
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Configure proxy if exist
        if self.proxy_config:
            proxy_url = self.proxy_config.get("server")
            if proxy_url:
                options.add_argument(f"--proxy-server={proxy_url}")

        # Create driver
        print("Initializing Chrome driver...")
        self.driver = webdriver.Chrome(options=options)

        print("Selenium driver configured successfully!")

    def navigate(self, url: str):
        """Navigate to a URL"""
        if self.driver:
            print(f"Navigating to: {url}")
            self.driver.get(url)
            time.sleep(5)  # Wait for loading

    def execute_script(self, script: str):
        """Execute a JavaScript script"""
        if self.driver:
            print(f"Executing script: {script[:50]}...")
            self.driver.execute_script(script)
            time.sleep(2)

    def click_element(self, selector: str):
        """Click on an element"""
        if self.driver and self.wait:
            try:
                element = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                element.click()
                print(f"Clicked on: {selector}")
            except Exception as e:
                print(f"Error clicking on {selector}: {e}")

    def wait_for_element(self, selector: str, timeout: int = 10):
        """Wait for an element to appear"""
        if self.driver:
            try:
                self.wait.timeout = timeout
                element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"Element found: {selector}")
                return element
            except Exception as e:
                print(f"Timeout waiting for element {selector}: {e}")
                return None
        return None

    def get_page_title(self) -> str:
        """Get the page title"""
        if self.driver:
            return self.driver.title
        return ""

    def get_current_url(self) -> str:
        """Get the current URL"""
        if self.driver:
            return self.driver.current_url
        return ""

    def add_cookies(self, cookies: list):
        """Add cookies"""
        if self.driver:
            print("Adding cookies from session...")

            self.driver.delete_all_cookies()
            time.sleep(1)

            # Adicionar cookies
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                    print(f"Cookie added: {cookie.get('name')}")
                except Exception as e:
                    print(f"Error adding cookie {cookie.get('name')}: {e}")

            print(f"Total cookies added: {len(cookies)}")

    def delete_all_cookies(self):
        """Remove all cookies"""
        if self.driver:
            print("Removing all cookies...")
            self.driver.delete_all_cookies()
            time.sleep(1)

    def get_cookie(self, name: str):
        """Get a specific cookie"""
        if self.driver:
            return self.driver.get_cookie(name)
        return None

    def get_cookies(self):
        """Get all cookies"""
        if self.driver:
            return self.driver.get_cookies()
        return []

    def implicit_wait(self, seconds: int):
        """Configure implicit wait"""
        if self.driver:
            self.driver.implicitly_wait(seconds)
            print(f"Implicit wait configured for {seconds} seconds")

    def close(self):
        """Close the driver"""
        if self.driver:
            print("Closing Selenium driver...")
            self.driver.quit()
            self.driver = None
            print("Driver closed")

    def get_driver_info(self) -> Dict[str, Any]:
        """Get driver information"""
        if self.driver:
            return {
                "current_url": self.driver.current_url,
                "title": self.driver.title,
                "cookies_count": len(self.driver.get_cookies()),
                "window_size": self.driver.get_window_size(),
                "page_source_length": len(self.driver.page_source),
            }
        return {}
