"""
Alter Python Client Library

The official Python client for the Alter AI API.
"""

from . import types
from ._types import NOT_GIVEN, Omit, NoneType, NotGiven, Transport, ProxiesTypes
from ._client import Alter, Client, Stream, Timeout, AsyncAlter, AsyncClient, AsyncStream, RequestOptions
from ._models import BaseModel
from ._version import __title__, __version__
from ._response import APIResponse, AsyncAPIResponse
from ._constants import DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES, DEFAULT_CONNECTION_LIMITS
from ._exceptions import (
    APIError,
    AlterError,
    ConflictError,
    NotFoundError,
    APIStatusError,
    RateLimitError,
    APITimeoutError,
    BadRequestError,
    APIConnectionError,
    AuthenticationError,
    InternalServerError,
    PermissionDeniedError,
    UnprocessableEntityError,
    APIResponseValidationError,
)
from ._base_client import DefaultHttpxClient, DefaultAsyncHttpxClient

__all__ = [
    "types",
    "__version__",
    "__title__",
    "NoneType",
    "Transport",
    "ProxiesTypes",
    "NotGiven",
    "NOT_GIVEN",
    "Omit",
    "AlterError",
    "APIError",
    "APIStatusError",
    "APITimeoutError",
    "APIConnectionError",
    "APIResponseValidationError",
    "BadRequestError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ConflictError",
    "UnprocessableEntityError",
    "RateLimitError",
    "InternalServerError",
    "Timeout",
    "RequestOptions",
    "Client",
    "AsyncClient",
    "Stream",
    "AsyncStream",
    "Alter",
    "AsyncAlter",
    "BaseModel",
    "APIResponse",
    "AsyncAPIResponse",
    "DEFAULT_TIMEOUT",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_CONNECTION_LIMITS",
    "DefaultHttpxClient",
    "DefaultAsyncHttpxClient",
]

# Update the __module__ attribute for exported symbols
__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        try:
            __locals[__name].__module__ = "alter"
        except (TypeError, AttributeError):
            # Some symbols are builtins which we can't set attributes for
            pass