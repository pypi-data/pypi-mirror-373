"""
Core of Whom Integration library
"""

import time
import requests
from typing import Dict, List, Optional, Any
from .exceptions import AuthenticationError, ConfigurationError
from .drivers import BaseDriver
from .systems import BaseSystem


class WhomClient:
    """
    Main client for Whom API integration
    """

    def __init__(
        self, token: str, extension_id: str, base_url: str = "https://cloud.doc9.com.br"
    ):
        """
        Initialize the Whom client

        Args:
            token: Authentication token
            extension_id: Extension ID
            base_url: Base URL of the API (default: cloud.doc9.com.br)
        """
        self.token = token
        self.extension_id = extension_id
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/auth"

        # Default headers
        self.headers = {
            "Content-Type": "application/json",
            "user-agent-whom": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }

        # HTTP session
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def authenticate(self, system: str = None, custom_headers: Dict = None) -> Dict:
        """
        Authenticate with Whom API

        Args:
            system: Specific system (optional)
            custom_headers: Custom headers (optional)

        Returns:
            Authenticated session data

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            # Prepare payload
            payload = {"token": self.token, "extension_id": self.extension_id}

            # Add custom headers if provided
            headers = self.headers.copy()
            if custom_headers:
                headers.update(custom_headers)

            # Initial request
            print("Starting authentication...")
            response = self.session.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            print(f"Initial response: {data.get('description')}")

            if not data.get("success"):
                error_msg = data.get("data", {}).get("message", "Erro desconhecido")
                raise AuthenticationError(f"Authentication failed: {error_msg}")

            # Verify if need to wait for processing
            if data.get("description") == "requestid":
                request_id = data.get("data", {}).get("request_id")
                print(f"Waiting for processing... Request ID: {request_id}")

                # Polling until receiving session
                while True:
                    time.sleep(5)
                    params = {
                        "extension_id": self.extension_id,
                        "request_id": request_id,
                    }
                    response = self.session.get(
                        self.api_url, headers=headers, params=params
                    )
                    data = response.json()

                    if data.get("description") == "session":
                        print("Session obtained successfully!")
                        break
                    elif not data.get("success"):
                        error_msg = data.get("data", {}).get(
                            "message", "Erro desconhecido"
                        )
                        raise AuthenticationError(
                            f"Error during processing: {error_msg}"
                        )
                    else:
                        print(f"Status: {data.get('data', {}).get('message')}")
            print(data.get("data"))
            return data.get("data")

        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Connection error: {e}")
        except Exception as e:
            raise AuthenticationError(f"Unexpected error: {e}")

    def create_session(
        self, system_class: type, driver_class: type, **kwargs
    ) -> "WhomSession":
        """
        Create an integration session

        Args:
            system_class: System class (ex: ECACSystem)
            driver_class: Driver class (ex: SeleniumDriver)
            **kwargs: Additional arguments for system and driver

        Returns:
            WhomSession instance
        """
        return WhomSession(self, system_class, driver_class, **kwargs)


class WhomSession:
    """
    Specific system integration session
    """

    def __init__(
        self, client: WhomClient, system_class: type, driver_class: type, **kwargs
    ):
        """
        Initialize the session

        Args:
            client: Cliente Whom
            system_class: System class
            driver_class: Driver class
            **kwargs: Arguments for system and driver
        """
        self.client = client
        self.system = system_class(**kwargs)
        self.driver = driver_class(**kwargs)
        self.session_data = None

    def authenticate_and_connect(self, system: str = None, custom_headers: Dict = None):
        """
        Authenticate and connect to the system

        Args:
            system: Specific system (optional)
            custom_headers: Custom headers (optional)
        """
        # 1. Authenticate with Whom
        self.session_data = self.client.authenticate(system, custom_headers)

        # 2. Configure driver
        self.driver.setup(
            self.session_data, self.client.token, self.client.extension_id
        )

        # 3. Configure system
        self.system.setup(self.session_data, self.driver)

        return self

    def execute_workflow(self, workflow_name: str = "default", **kwargs):
        """
        Execute a specific workflow

        Args:
            workflow_name: Workflow name
            **kwargs: Workflow arguments
        """
        return self.system.execute_workflow(workflow_name, **kwargs)

    def close(self):
        """Close the session"""
        if self.driver:
            self.driver.close()
        print("Session closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
