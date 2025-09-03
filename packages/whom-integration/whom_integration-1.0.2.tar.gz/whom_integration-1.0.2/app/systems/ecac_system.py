"""
ECAC system for Whom integration
"""

import time
from typing import Dict, Any
from .base import BaseSystem


class ECACSystem(BaseSystem):
    """
    Specific system for ECAC (Receita Federal)
    """

    def __init__(self, **kwargs):
        """
        Initialize the ECAC system

        Args:
            **kwargs: Specific ECAC configurations
        """
        super().__init__(**kwargs)
        self.system_name = "ECAC"
        self.entry_point = kwargs.get("entry_point")

    def setup(self, session_data: Dict, driver):
        """
        Configure the ECAC system

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

    def execute_workflow(self, workflow_name: str = "default", **kwargs):
        """
        Execute a specific ECAC workflow

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
        Default workflow for ECAC
        """
        print("Executing default workflow for ECAC...")

        try:
            # 1. Navigate to redirect URL
            self.navigate_to_redirect()
            time.sleep(3)

            # 2. Execute JavaScript commands
            self.execute_js_commands()

            # 3. Wait and verify authentication
            time.sleep(5)

            # 8. Capture final information
            final_info = self.get_system_info()

            return {"success": True, "status": "completed", "final_info": final_info}

        except Exception as e:
            print(f"Error during workflow: {e}")
            return {"success": False, "status": "error", "error": str(e)}

    def get_ecac_specific_info(self) -> Dict[str, Any]:
        """
        Get specific ECAC information

        Returns:
            Dictionary with specific information
        """
        base_info = self.get_system_info()

        ecac_info = {
            "system_name": self.system_name,
            "entry_point": self.entry_point,
        }

        return {**base_info, **ecac_info}

    def get_js_commands(self) -> list:
        """
        Get JavaScript commands

        Returns:
            List of JavaScript commands
        """
        if self.session_data:
            js_commands = self.session_data.get("js", [])
            js_commands.append(
                {"comando": "click", "local": "input[alt='Acesso Gov BR']"}
            )
            return js_commands
        return []
