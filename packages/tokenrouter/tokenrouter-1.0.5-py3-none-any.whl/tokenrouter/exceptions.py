"""
TokenRouter SDK Exceptions
"""

from typing import Optional, Dict, Any


class TokenRouterError(Exception):
    """Base exception for TokenRouter SDK errors"""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response
        self.headers = headers


class AuthenticationError(TokenRouterError):
    """Raised when authentication fails"""
    pass


class RateLimitError(TokenRouterError):
    """Raised when rate limit is exceeded"""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        retry_after: Optional[int] = None,
    ):
        super().__init__(message, status_code, response, headers)
        self.retry_after = retry_after


class InvalidRequestError(TokenRouterError):
    """Raised when the request is invalid"""
    pass


class APIConnectionError(TokenRouterError):
    """Raised when connection to the API fails"""
    pass


class APIStatusError(TokenRouterError):
    """Raised when the API returns a non-success status code"""
    pass


class TimeoutError(TokenRouterError):
    """Raised when a request times out"""
    pass


class QuotaExceededError(TokenRouterError):
    """Raised when the user's quota is exceeded"""
    pass