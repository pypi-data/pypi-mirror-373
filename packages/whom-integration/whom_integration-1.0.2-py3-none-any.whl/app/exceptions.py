"""
Custom exceptions for Whom Integration
"""


class WhomError(Exception):
    """Base exception for all Whom library errors"""

    pass


class AuthenticationError(WhomError):
    """Authentication error with Whom API"""

    pass


class ProxyError(WhomError):
    """Proxy related error"""

    pass


class DriverError(WhomError):
    """Driver related error (Selenium/Playwright)"""

    pass


class SystemError(WhomError):
    """Specific system related error (ECAC, etc.)"""

    pass


class ConfigurationError(WhomError):
    """Configuration error"""

    pass


class TimeoutError(WhomError):
    """Timeout error"""

    pass
