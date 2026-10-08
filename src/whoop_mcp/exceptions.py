class WhoopError(Exception):
    """Base exception for WHOOP integration errors."""


class WhoopAuthenticationError(WhoopError):
    """Raised when WHOOP authentication fails."""


class WhoopAPIError(WhoopError):
    """Raised when a WHOOP API request fails."""


class WhoopConfigurationError(WhoopError):
    """Raised when required WHOOP configuration is missing."""