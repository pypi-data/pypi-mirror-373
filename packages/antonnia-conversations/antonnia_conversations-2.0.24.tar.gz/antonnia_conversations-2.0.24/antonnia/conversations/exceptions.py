"""
Antonnia SDK Exceptions

Custom exception classes for handling API errors and client-side issues.
"""

from typing import Any, Dict, Optional


class AntonniaError(Exception):
    """Base exception for all Antonnia SDK errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class AuthenticationError(AntonniaError):
    """Raised when authentication fails (401 Unauthorized)."""
    pass


class NotFoundError(AntonniaError):
    """Raised when a resource is not found (404 Not Found)."""
    pass


class ValidationError(AntonniaError):
    """Raised when request validation fails (422 Unprocessable Entity)."""
    pass


class RateLimitError(AntonniaError):
    """Raised when rate limit is exceeded (429 Too Many Requests)."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class APIError(AntonniaError):
    """Raised for other API errors (5xx Server Errors and other 4xx Client Errors)."""
    pass


def create_error_from_response(status_code: int, response_data: Dict[str, Any]) -> AntonniaError:
    """
    Create appropriate exception based on HTTP status code.
    
    Args:
        status_code: HTTP status code from the response
        response_data: Response body data
        
    Returns:
        Appropriate exception instance
    """
    message = response_data.get("detail", f"HTTP {status_code} error")
    
    if status_code == 401:
        return AuthenticationError(message, status_code, response_data)
    elif status_code == 404:
        return NotFoundError(message, status_code, response_data)
    elif status_code == 422:
        return ValidationError(message, status_code, response_data)
    elif status_code == 429:
        retry_after = response_data.get("retry_after")
        return RateLimitError(message, retry_after, status_code=status_code, response_data=response_data)
    elif 400 <= status_code < 500:
        return APIError(message, status_code, response_data)
    elif 500 <= status_code < 600:
        return APIError(message, status_code, response_data)
    else:
        return AntonniaError(message, status_code, response_data) 