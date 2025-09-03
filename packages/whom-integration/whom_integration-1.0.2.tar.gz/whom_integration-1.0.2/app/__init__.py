"""
Whom Integration Library

Versatile Python library for Whom API integration, supporting multiple systems 
and web automation drivers.

This library provides a unified interface for integrating with various government
systems like ECAC (Federal Revenue) and PJE (Judiciary) using different automation
drivers including Selenium and Playwright.
"""

__version__ = "1.0.2"
__author__ = "Doc9"
__email__ = "cloud@doc9.com.br"
__license__ = "MIT"
__url__ = "https://github.com/doc9/whom-integration"

# Core classes
from .core import WhomClient, WhomSession

# Systems
from .systems.ecac_system import ECACSystem
from .systems.pje_system import PJESystem

# Drivers
from .drivers.selenium_driver import SeleniumDriver
from .drivers.playwright_driver import PlaywrightDriver

# Exceptions
from .exceptions import (
    WhomError,
    AuthenticationError,
    DriverError,
    SystemError,
)

# Version info
__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__url__",
    "WhomClient",
    "WhomSession",
    "ECACSystem",
    "PJESystem",
    "SeleniumDriver",
    "PlaywrightDriver",
    "WhomError",
    "AuthenticationError",
    "DriverError",
    "SystemError",
]
