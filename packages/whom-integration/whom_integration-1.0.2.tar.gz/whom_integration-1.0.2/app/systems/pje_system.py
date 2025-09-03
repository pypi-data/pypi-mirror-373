"""
PJE system for Whom integration
"""

import time
from typing import Dict, Any, Optional
from .base import BaseSystem


class PJESystem(BaseSystem):
    """
    Specific system for PJE (Poder Judiciário Eletrônico)
    """

    def __init__(self, **kwargs):
        """
        Initialize the PJE system

        Args:
            **kwargs: Specific PJE configurations
        """
        super().__init__(**kwargs)
        self.system_name = "PJE"
        self.entry_point = kwargs.get("entry_point", "https://pje2g.trf1.jus.br/pje")
        self.wait_time = kwargs.get("wait_time", 5)

    def setup(self, session_data: Dict, driver):
        """
        Configure the PJE system

        Args:
            session_data: Session data
            driver: Configured driver
        """
        self.session_data = session_data
        self.driver = driver

        print(f"🎯 System {self.system_name} configured")
        print(f"🔄 Redirect URL: {self.get_redirect_url()}")
        print(f"🎯 Target URL: {self.get_target_url()}")
        print(f"🍪 Cookies: {len(self.get_cookies())} found")
        print(f"🔧 JS commands: {len(self.get_js_commands())} found")
        print(f"📍 Entry Point: {self.entry_point}")

    def execute_workflow(self, workflow_name: str = "default", **kwargs):
        """
        Execute a specific PJE workflow

        Args:
            workflow_name: Workflow name
            **kwargs: Workflow arguments

        Returns:
            Execution result
        """
        if workflow_name == "default":
            return self._execute_default_workflow(**kwargs)
        else:
            print(f"Workflow '{workflow_name}' not implemented")
            return None

    def _execute_default_workflow(self, **kwargs):
        """
        Default workflow for PJE
        """
        print("Executing default workflow for PJE...")

        try:
            # 1. Navigate to entry point
            print(f"Navigating to entry point: {self.entry_point}")
            self.driver.navigate(self.entry_point)
            time.sleep(self.wait_time)

            # 2. Add cookies from session
            print("Adding cookies from session...")
            cookies = self.get_cookies()
            self.driver.add_cookies(cookies)

            # 3. Navigate to redirect URL
            self.navigate_to_redirect()
            self.driver.driver.implicitly_wait(10)

            # 4. Verify authentication status
            time.sleep(self.wait_time)
            current_url = self.driver.get_current_url()
            title = self.driver.get_page_title()

            print(f"Current URL: {current_url}")
            print(f"Page title: {title}")

            # 5. Verify if authentication was successful
            auth_status = self._check_pje_authentication_status(current_url)

            # 6. Capture final information
            final_info = self.get_system_info()

            return {
                "success": auth_status["success"],
                "status": auth_status["status"],
                "auth_details": auth_status,
                "final_info": final_info,
            }

        except Exception as e:
            print(f"Error during workflow: {e}")
            return {"success": False, "status": "error", "error": str(e)}

    def _check_pje_authentication_status(self, current_url: str) -> Dict[str, Any]:
        """
        Verify PJE authentication status

        Args:
            current_url: Current URL

        Returns:
            Dictionary with authentication status
        """
        if "login.seam" in current_url:
            print("Login required. Session was not authenticated with cookies.")
            return {
                "success": False,
                "status": "login_required",
                "reason": "login.seam detected in URL",
            }
        else:
            print("Login recognized successfully.")
            return {
                "success": True,
                "status": "authenticated",
                "reason": "No login page detected",
            }

    def _check_pje_success_indicators(self) -> Dict[str, Any]:
        """
        Verify specific PJE success indicators

        Returns:
            Dictionary with success indicators
        """
        indicators = {}

        try:
            # Search for elements that indicate success in PJE
            success_selectors = [
                "//a[contains(text(), 'Sair')]",
                "//a[contains(text(), 'Logout')]",
                "//span[contains(text(), 'Bem-vindo')]",
                "//div[contains(@class, 'usuario')]",
                "//span[contains(text(), 'PJE')]",
            ]

            for selector in success_selectors:
                try:
                    element = self.driver.wait_for_element(selector, timeout=5000)
                    if element:
                        indicators[selector] = True
                        print(f"Success indicator found: {selector}")
                    else:
                        indicators[selector] = False

                except Exception:
                    indicators[selector] = False

            # Verify if there are specific PJE elements
            current_url = self.driver.get_current_url()
            title = self.driver.get_page_title()

            indicators["url_contains_pje"] = "pje" in current_url.lower()
            indicators["title_contains_pje"] = "pje" in title.lower()

        except Exception as e:
            print(f"Error verifying indicators: {e}")

        return indicators

    def get_pje_specific_info(self) -> Dict[str, Any]:
        """
        Get specific PJE information

        Returns:
            Dictionary with specific information
        """
        base_info = self.get_system_info()

        # Add specific PJE information
        pje_info = {
            "system_name": self.system_name,
            "entry_point": self.entry_point,
            "wait_time": self.wait_time,
            "success_indicators": self._check_pje_success_indicators(),
        }

        return {**base_info, **pje_info}
