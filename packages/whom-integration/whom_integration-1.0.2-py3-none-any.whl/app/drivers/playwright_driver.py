"""
Playwright driver for web automation
"""

from typing import Dict
from patchright.sync_api import sync_playwright
from .base import BaseDriver


class PlaywrightDriver(BaseDriver):
    """
    Playwright driver for web automation
    """

    def __init__(self, **kwargs):
        """
        Initialize the Playwright driver

        Args:
            **kwargs: Specific Playwright configurations
        """
        super().__init__(**kwargs)
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def setup(self, session_data: Dict, token: str, extension_id: str):
        """
        Configure the Playwright driver

        Args:
            session_data: Session data
            token: Authentication token
            extension_id: Extension ID
        """
        # Start Playwright
        self.playwright = sync_playwright().start()

        # Configure browser
        browser_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-setuid-sandbox",
            "--disable-web-security",
            "--disable-dev-mode",  # disable dev mode
            "--disable-debug-mode",  # disable debug mode
        ]

        self.browser = self.playwright.chromium.launch(
            headless=False, args=browser_args
        )

        # Create context
        context_options = {
            "ignore_https_errors": True,
            "locale": "pt-BR",
            "bypass_csp": True,
        }

        self.context = self.browser.new_context(**context_options)

        # Add cookies if exist
        cookies = session_data.get("cookies", [])
        self.context.add_cookies(cookies)

        # Create page
        self.page = self.context.new_page()

    def navigate(self, url: str):
        """Navigate to a URL"""
        if self.page:
            self.page.goto(url, wait_until="domcontentloaded")

    def execute_script(self, script: str):
        """Execute a JavaScript script"""
        if self.page:
            self.page.evaluate(script)
            self.page.wait_for_timeout(2000)

    def click_element(self, selector: str):
        """Click on an element"""
        if self.page:
            self.page.click(selector)

    def wait_for_element(self, selector: str, timeout: int = 10000):
        """Wait for an element to appear"""
        if self.page:
            element = self.page.wait_for_selector(selector, timeout=timeout)
            return element
        return None

    def get_page_title(self) -> str:
        """Get the page title"""
        if self.page:
            return self.page.title()
        return ""

    def get_current_url(self) -> str:
        """Get the current URL"""
        if self.page:
            return self.page.url
        return ""

    def add_cookies(self, cookies: list):
        """Add cookies"""
        if self.context:
            for cookie in cookies:
                try:
                    cookie_dict = {
                        "name": cookie.get("name"),
                        "value": cookie.get("value"),
                        "domain": cookie.get("domain"),
                        "path": cookie.get("path", "/"),
                        "secure": cookie.get("secure", False),
                        "httpOnly": cookie.get("httpOnly", False),
                    }

                    self.context.add_cookies([cookie_dict])
                except Exception as e:
                    print(f"Error adding cookie {cookie.get('name')}: {e}")

    def close(self):
        """Close the driver"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
