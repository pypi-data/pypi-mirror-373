"""Custom exceptions for the tmdbone library for predictable error handling."""

class TMDbException(Exception):
    """Base exception for all errors raised by the tmdbone library."""
    pass

class TMDbAPIError(TMDbException):
    """
    Raised when an API request fails after all retries due to a persistent
    server-side or network issue.
    """
    def __init__(self, message: str, status_code: int = None, url: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.url = url
    
    def __str__(self) -> str:
        return f"{super().__str__()} (Status: {self.status_code}, URL: {self.url})"