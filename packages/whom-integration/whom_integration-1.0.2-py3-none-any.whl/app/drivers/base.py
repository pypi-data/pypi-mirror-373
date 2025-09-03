"""
Base class for automation drivers
"""

from abc import ABC, abstractmethod
from typing import Dict


class BaseDriver(ABC):
    """
    Base class for automation drivers
    """

    def __init__(self, **kwargs):
        """
        Initialize the driver

        Args:
            **kwargs: Specific driver configurations
        """
        self.driver = None
        self.page = None
        self.config = kwargs
        self.proxy_config = None
        self.proxy_headers = {}

    @abstractmethod
    def setup(self, session_data: Dict, token: str, extension_id: str):
        """
        Configure the driver with session data

        Args:
            session_data: Session data
            token: Authentication token
            extension_id: Extension ID
        """
        pass

    @abstractmethod
    def navigate(self, url: str):
        """
        Navigate to a URL

        Args:
            url: URL to navigate to
        """
        pass

    @abstractmethod
    def execute_script(self, script: str):
        """
        Execute a JavaScript script

        Args:
            script: Script to execute
        """
        pass

    @abstractmethod
    def click_element(self, selector: str):
        """
        Click on an element

        Args:
            selector: Selector of the element
        """
        pass

    @abstractmethod
    def wait_for_element(self, selector: str, timeout: int = 10):
        """
        Wait for an element to appear

        Args:
            selector: Selector of the element
            timeout: Timeout em segundos
        """
        pass

    @abstractmethod
    def get_page_title(self) -> str:
        """
        Get the page title

        Returns:
            Page title
        """
        pass

    @abstractmethod
    def get_current_url(self) -> str:
        """
        Get the current URL

        Returns:
            Current URL
        """
        pass

    @abstractmethod
    def add_cookies(self, cookies: list):
        """
        Add cookies

        Args:
            cookies: List of cookies
        """
        pass

    @abstractmethod
    def close(self):
        """Close the driver"""
        pass
