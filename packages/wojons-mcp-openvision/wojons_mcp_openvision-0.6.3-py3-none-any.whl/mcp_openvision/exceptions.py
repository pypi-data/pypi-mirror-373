"""
Exceptions for MCP OpenVision.
"""


class OpenVisionError(Exception):
    """Base exception for MCP OpenVision errors."""

    pass


class ConfigurationError(OpenVisionError):
    """Exception raised for configuration errors."""

    pass


class OpenRouterError(OpenVisionError):
    """Exception raised for OpenRouter API errors."""

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(f"OpenRouter API error ({status_code}): {message}")
