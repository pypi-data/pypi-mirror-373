"""Exception classes for the Alter Python client."""

from typing import Any, Dict, Optional, Type, Union, cast
import httpx


class AlterError(Exception):
    """Base exception class for the Alter client."""
    pass


class APIError(AlterError):
    """Base class for API-related errors."""
    
    def __init__(self, message: str, *, request: Optional[httpx.Request] = None, body: Optional[object] = None) -> None:
        super().__init__(message)
        self.request = request
        self.body = body


class APIStatusError(APIError):
    """Raised when an API response has an unsuccessful status code."""
    
    def __init__(
        self,
        message: str,
        *,
        response: httpx.Response,
        body: Optional[object] = None,
    ) -> None:
        super().__init__(message, request=response.request, body=body)
        self.response = response
    
    @property 
    def status_code(self) -> int:
        return self.response.status_code


class APIConnectionError(APIError):
    """Raised when an API request fails due to a connection error."""
    
    def __init__(self, *, request: Optional[httpx.Request] = None) -> None:
        super().__init__("Connection error.", request=request)


class APITimeoutError(APIConnectionError):
    """Raised when an API request times out."""
    
    def __init__(self, *, request: Optional[httpx.Request] = None) -> None:
        super().__init__(request=request)
        self.args = ("Request timed out.",)


class APIResponseValidationError(APIError):
    """Raised when we fail to parse the API response."""
    
    def __init__(
        self,
        *,
        response: httpx.Response,
        body: Optional[object] = None,
        message: str = "Data validation error",
    ) -> None:
        super().__init__(message, request=response.request, body=body)
        self.response = response


# HTTP status code specific errors
class BadRequestError(APIStatusError):
    """400 Bad Request"""
    pass


class AuthenticationError(APIStatusError):
    """401 Unauthorized"""
    pass


class PermissionDeniedError(APIStatusError):
    """403 Forbidden"""
    pass


class NotFoundError(APIStatusError):
    """404 Not Found"""
    pass


class ConflictError(APIStatusError):
    """409 Conflict"""
    pass


class UnprocessableEntityError(APIStatusError):
    """422 Unprocessable Entity"""
    pass


class RateLimitError(APIStatusError):
    """429 Too Many Requests"""
    pass


class InternalServerError(APIStatusError):
    """500+ Internal Server Error"""
    pass


def make_status_error_from_response(response: httpx.Response) -> APIStatusError:
    """Create an appropriate status error from an HTTP response."""
    
    err_msg = f"Error code: {response.status_code}"
    err_body = None
    
    try:
        err_body = response.json()
        if isinstance(err_body, dict):
            err_msg = err_body.get("message", err_body.get("error", err_msg))
    except Exception:
        err_msg = response.text or err_msg
    
    if response.status_code == 400:
        return BadRequestError(err_msg, response=response, body=err_body)
    elif response.status_code == 401:
        return AuthenticationError(err_msg, response=response, body=err_body)
    elif response.status_code == 403:
        return PermissionDeniedError(err_msg, response=response, body=err_body)
    elif response.status_code == 404:
        return NotFoundError(err_msg, response=response, body=err_body)
    elif response.status_code == 409:
        return ConflictError(err_msg, response=response, body=err_body)
    elif response.status_code == 422:
        return UnprocessableEntityError(err_msg, response=response, body=err_body)
    elif response.status_code == 429:
        return RateLimitError(err_msg, response=response, body=err_body)
    elif response.status_code >= 500:
        return InternalServerError(err_msg, response=response, body=err_body)
    else:
        return APIStatusError(err_msg, response=response, body=err_body)