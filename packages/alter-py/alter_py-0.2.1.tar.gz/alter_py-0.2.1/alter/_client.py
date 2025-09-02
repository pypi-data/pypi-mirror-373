"""Main client classes for the Alter Python client."""

import os
import ssl
from typing import Optional, Union, Dict, Any
import httpx

from ._types import NOT_GIVEN, NotGiven, RequestOptions, Transport, ProxiesTypes
from ._constants import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES
from ._base_client import DefaultHttpxClient, DefaultAsyncHttpxClient
from .resources import (
    HealthResource,
    AsyncHealthResource,
    MCPServers,
    AsyncMCPServers,
    MCPPools,
    AsyncMCPPools,
)

__all__ = [
    "Client",
    "AsyncClient", 
    "Alter",
    "AsyncAlter",
    "Stream",
    "AsyncStream",
    "Timeout",
    "Transport",
    "RequestOptions",
]

# Type aliases
Timeout = Union[float, httpx.Timeout, None, NotGiven]
Stream = httpx.Response  # Placeholder for streaming
AsyncStream = httpx.Response  # Placeholder for async streaming


class Client(DefaultHttpxClient):
    """Synchronous Alter API client."""
    
    health: HealthResource
    mcp: MCPServers
    pools: MCPPools
    
    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Timeout = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        custom_headers: Optional[Dict[str, str]] = None,
        custom_query: Optional[Dict[str, Any]] = None,
        proxies: Optional[ProxiesTypes] = None,
        transport: Optional[Transport] = None,
        verify: Union[str, bool, ssl.SSLContext] = True,
        **kwargs: Any,
    ) -> None:
        """Initialize the Alter client.
        
        Args:
            api_key: Your Alter API key. If not provided, will look for ALTER_API_KEY environment variable.
            base_url: Base URL for the Alter API. If not provided, will look for ALTER_BASE_URL environment variable,
                     then fall back to default.
            timeout: Request timeout configuration.
            max_retries: Maximum number of request retries.
            custom_headers: Additional headers to send with requests.
            custom_query: Additional query parameters to send with requests.
            proxies: Proxy configuration.
            transport: Custom transport implementation.
            verify: SSL verification configuration.
        """
        if api_key is None:
            api_key = os.environ.get("ALTER_API_KEY")
            if api_key is None:
                raise ValueError(
                    "API key must be provided either as argument or ALTER_API_KEY environment variable"
                )
        
        if base_url is None:
            base_url = os.environ.get("ALTER_BASE_URL", DEFAULT_BASE_URL)
        
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            custom_headers=custom_headers,
            custom_query=custom_query,
            proxies=proxies,
            transport=transport,
            verify=verify,
            **kwargs,
        )
        
        # Initialize resources
        self.health = HealthResource(self)
        self.mcp = MCPServers(self)
        self.pools = MCPPools(self)
    
    def with_options(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[Timeout] = None,
        max_retries: Optional[int] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        custom_query: Optional[Dict[str, Any]] = None,
        proxies: Optional[ProxiesTypes] = None,
        transport: Optional[Transport] = None,
        verify: Optional[Union[str, bool, ssl.SSLContext]] = None,
    ) -> "Client":
        """Create a new client with modified options."""
        return Client(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=timeout if timeout is not None else self.timeout,
            max_retries=max_retries if max_retries is not None else self.max_retries,
            custom_headers=custom_headers or self._custom_headers,
            custom_query=custom_query or self._custom_query,
            proxies=proxies if proxies is not None else self._proxies,
            transport=transport if transport is not None else self._transport,
            verify=verify if verify is not None else self._verify,
        )


class AsyncClient(DefaultAsyncHttpxClient):
    """Asynchronous Alter API client."""
    
    health: AsyncHealthResource
    mcp: AsyncMCPServers
    pools: AsyncMCPPools
    
    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Timeout = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        custom_headers: Optional[Dict[str, str]] = None,
        custom_query: Optional[Dict[str, Any]] = None,
        proxies: Optional[ProxiesTypes] = None,
        transport: Optional[Transport] = None,
        verify: Union[str, bool, ssl.SSLContext] = True,
        **kwargs: Any,
    ) -> None:
        """Initialize the async Alter client.
        
        Args:
            api_key: Your Alter API key. If not provided, will look for ALTER_API_KEY environment variable.
            base_url: Base URL for the Alter API. If not provided, will look for ALTER_BASE_URL environment variable,
                     then fall back to default.
            timeout: Request timeout configuration.
            max_retries: Maximum number of request retries.
            custom_headers: Additional headers to send with requests.
            custom_query: Additional query parameters to send with requests.
            proxies: Proxy configuration.
            transport: Custom transport implementation.
            verify: SSL verification configuration.
        """
        if api_key is None:
            api_key = os.environ.get("ALTER_API_KEY")
            if api_key is None:
                raise ValueError(
                    "API key must be provided either as argument or ALTER_API_KEY environment variable"
                )
        
        if base_url is None:
            base_url = os.environ.get("ALTER_BASE_URL", DEFAULT_BASE_URL)
        
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            custom_headers=custom_headers,
            custom_query=custom_query,
            proxies=proxies,
            transport=transport,
            verify=verify,
            **kwargs,
        )
        
        # Initialize resources
        self.health = AsyncHealthResource(self)
        self.mcp = AsyncMCPServers(self)
        self.pools = AsyncMCPPools(self)
    
    def with_options(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[Timeout] = None,
        max_retries: Optional[int] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        custom_query: Optional[Dict[str, Any]] = None,
        proxies: Optional[ProxiesTypes] = None,
        transport: Optional[Transport] = None,
        verify: Optional[Union[str, bool, ssl.SSLContext]] = None,
    ) -> "AsyncClient":
        """Create a new async client with modified options."""
        return AsyncClient(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=timeout if timeout is not None else self.timeout,
            max_retries=max_retries if max_retries is not None else self.max_retries,
            custom_headers=custom_headers or self._custom_headers,
            custom_query=custom_query or self._custom_query,
            proxies=proxies if proxies is not None else self._proxies,
            transport=transport if transport is not None else self._transport,
            verify=verify if verify is not None else self._verify,
        )


# Convenience aliases
Alter = Client
AsyncAlter = AsyncClient