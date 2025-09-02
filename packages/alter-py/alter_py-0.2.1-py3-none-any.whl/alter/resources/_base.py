"""Base resource classes."""

from typing import TYPE_CHECKING, Any, Type, TypeVar

if TYPE_CHECKING:
    from .._base_client import DefaultHttpxClient, DefaultAsyncHttpxClient

_T = TypeVar("_T")


class BaseResource:
    """Base class for API resources."""
    
    def __init__(self, client: "DefaultHttpxClient") -> None:
        self._client = client
    
    def _request(
        self,
        method: str,
        path: str,
        *,
        cast_to: Type[_T],
        body: Any = None,
        params: Any = None,
        options: Any = None,
    ) -> _T:
        """Make a request using the client."""
        return self._client.request(
            method=method,
            path=path,
            cast_to=cast_to,
            body=body,
            params=params,
            options=options,
        )


class AsyncBaseResource:
    """Base class for async API resources."""
    
    def __init__(self, client: "DefaultAsyncHttpxClient") -> None:
        self._client = client
    
    async def _request(
        self,
        method: str,
        path: str,
        *,
        cast_to: Type[_T],
        body: Any = None,
        params: Any = None,
        options: Any = None,
    ) -> _T:
        """Make an async request using the client."""
        return await self._client.request(
            method=method,
            path=path,
            cast_to=cast_to,
            body=body,
            params=params,
            options=options,
        )