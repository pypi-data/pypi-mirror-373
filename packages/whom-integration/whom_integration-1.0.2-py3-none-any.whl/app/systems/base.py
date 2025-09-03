"""
Base class for supported systems
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..drivers import BaseDriver


class BaseSystem(ABC):
    """
    Base abstract class for supported systems
    """

    def __init__(self, **kwargs):
        """
        Initialize the system

        Args:
            **kwargs: Specific system configurations
        """
        self.config = kwargs
        self.driver = None
        self.session_data = None

    @abstractmethod
    def setup(self, session_data: Dict, driver: BaseDriver):
        """
        Configure the system with session data

        Args:
            session_data: Session data
            driver: Configured driver
        """
        pass

    @abstractmethod
    def execute_workflow(self, workflow_name: str = "default", **kwargs):
        """
        Execute a specific workflow

        Args:
            workflow_name: Workflow name
            **kwargs: Workflow arguments

        Returns:
            Execution result
        """
        pass

    def get_redirect_url(self) -> Optional[str]:
        """
        Get redirect URL

        Returns:
            Redirect URL or None
        """
        if self.session_data:
            return self.session_data.get("redirect")
        return None

    def get_target_url(self) -> Optional[str]:
        """
        Get target URL

        Returns:
            Target URL or None
        """
        if self.session_data:
            return self.session_data.get("target") or self.session_data.get("url")
        return None

    def get_js_commands(self) -> list:
        """
        Get JavaScript commands

        Returns:
            List of JavaScript commands
        """
        if self.session_data:
            return self.session_data.get("js", [])
        return []

    def get_cookies(self) -> list:
        """
        Get cookies from session

        Returns:
            List of cookies
        """
        if self.session_data:
            return self.session_data.get("cookies", [])
        return []

    def execute_js_commands(self):
        """
        Execute JavaScript commands from session
        """
        if not self.driver:
            return

        js_commands = self.get_js_commands()
        for command in js_commands:
            comando = command.get("comando")
            valor = command.get("valor")
            local = command.get("local")

            print(f"Executing command: {comando}")

            try:
                if comando == "proxy":
                    # Configuração de proxy - já foi tratada no driver
                    print(f"Proxy configuration: {valor.get('proxy')}")

                elif comando == "executeScript":
                    # Executar script JavaScript
                    print(f"📜 Executando script: {valor}")
                    self.driver.execute_script(valor)

                elif comando == "click":
                    # Clicar em elemento
                    self.driver.click_element(local)
                    print(f"Clicked on: {local}")

                elif comando == "waitElement":
                    # Aguardar elemento
                    selector = valor.get("local")
                    self.driver.wait_for_element(selector)
                    print(f"Element waited: {selector}")

                elif comando == "set":
                    # Definir valores no localStorage/sessionStorage
                    local = valor.get("local")
                    chave = valor.get("chave")
                    valor_set = valor.get("valor")

                    if local == "localstorage":
                        script = f"localStorage.setItem('{chave}', '{valor_set}')"
                        self.driver.execute_script(script)
                        print(f"LocalStorage defined: {chave} = {valor_set}")
                    elif local == "sessionstorage":
                        script = f"sessionStorage.setItem('{chave}', '{valor_set}')"
                        self.driver.execute_script(script)
                        print(f"SessionStorage defined: {chave} = {valor_set}")

                elif comando == "reload":
                    # Recarregar página
                    self.driver.navigate(self.driver.get_current_url())
                    print("Page reloaded")

                elif comando == "assign":
                    # Redirecionar para URL
                    url = valor
                    self.driver.navigate(url)
                    print(f"Redirected to: {url}")

                else:
                    print(f"Command not implemented: {comando}")

            except Exception as e:
                print(f"Error executing command {comando}: {e}")

    def navigate_to_redirect(self):
        """
        Navigate to redirect URL
        """
        redirect_url = self.get_redirect_url()
        if redirect_url and self.driver:
            print(f"Navigating to: {redirect_url}")
            self.driver.navigate(redirect_url)

    def navigate_to_target(self):
        """
        Navigate to target URL
        """
        target_url = self.get_target_url()
        if target_url and self.driver:
            print(f"Navigating to target URL: {target_url}")
            self.driver.navigate(target_url)

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information

        Returns:
            Dictionary with system information
        """
        return {
            "redirect_url": self.get_redirect_url(),
            "target_url": self.get_target_url(),
            "js_commands_count": len(self.get_js_commands()),
            "cookies_count": len(self.get_cookies()),
            "current_url": self.driver.get_current_url() if self.driver else None,
            "page_title": self.driver.get_page_title() if self.driver else None,
        }
