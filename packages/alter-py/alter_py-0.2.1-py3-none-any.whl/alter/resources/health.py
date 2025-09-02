"""Health resource implementation."""

from typing import Optional
from .._types import NOT_GIVEN, NotGiven, RequestOptions
from ..types.health import HealthResponse, DetailedHealthResponse
from ._base import BaseResource, AsyncBaseResource

__all__ = ["HealthResource", "AsyncHealthResource"]


class HealthResource(BaseResource):
    """Health resource for sync client."""
    
    def check(
        self,
        *,
        options: Optional[RequestOptions] = None,
    ) -> HealthResponse:
        """Basic health check."""
        return self._request(
            "GET",
            "/health",
            cast_to=HealthResponse,
            options=options,
        )
    
    def detailed(
        self,
        *,
        options: Optional[RequestOptions] = None,
    ) -> DetailedHealthResponse:
        """Detailed health check with dependencies."""
        return self._request(
            "GET",
            "/health/detailed",
            cast_to=DetailedHealthResponse,
            options=options,
        )


class AsyncHealthResource(AsyncBaseResource):
    """Health resource for async client."""
    
    async def check(
        self,
        *,
        options: Optional[RequestOptions] = None,
    ) -> HealthResponse:
        """Basic health check."""
        return await self._request(
            "GET",
            "/health",
            cast_to=HealthResponse,
            options=options,
        )
    
    async def detailed(
        self,
        *,
        options: Optional[RequestOptions] = None,
    ) -> DetailedHealthResponse:
        """Detailed health check with dependencies."""
        return await self._request(
            "GET",
            "/health/detailed",
            cast_to=DetailedHealthResponse,
            options=options,
        )