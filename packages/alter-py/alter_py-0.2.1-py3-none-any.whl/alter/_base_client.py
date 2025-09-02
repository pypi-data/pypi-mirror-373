"""Base HTTP client implementation for the Alter Python client."""

import os
import sys
import json
import time
import logging
import ssl
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from typing_extensions import override
import httpx

from ._types import (
    NOT_GIVEN,
    NotGiven,
    Headers,
    QueryParams,
    RequestOptions,
    ProxiesTypes,
    Transport,
)
from ._constants import (
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_CONNECTION_LIMITS,
    USER_AGENT,
)
from ._exceptions import (
    APIError,
    APIConnectionError,
    APITimeoutError,
    make_status_error_from_response,
)
from ._response import APIResponse, AsyncAPIResponse
from ._models import BaseModel

__all__ = ["DefaultHttpxClient", "DefaultAsyncHttpxClient"]

_T = TypeVar("_T")

log = logging.getLogger(__name__)


class BaseClient:
    """Base client class with common functionality."""
    
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        custom_headers: Optional[Dict[str, str]] = None,
        custom_query: Optional[Dict[str, Any]] = None,
        proxies: Optional[ProxiesTypes] = None,
        transport: Optional[Transport] = None,
        verify: Union[str, bool, ssl.SSLContext] = True,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self._custom_headers = custom_headers or {}
        self._custom_query = custom_query or {}
        self._proxies = proxies
        self._transport = transport
        self._verify = verify
        
        if isinstance(timeout, NotGiven):
            self.timeout = DEFAULT_TIMEOUT
        else:
            self.timeout = timeout
    
    def _build_headers(self, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build request headers."""
        headers = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
        # Add custom headers
        headers.update(self._custom_headers)
        
        # Add extra headers
        if extra_headers:
            headers.update(extra_headers)
        
        return headers
    
    def _build_url(self, path: str) -> str:
        """Build the full URL for a request."""
        return f"{self.base_url}{path}"
    
    def _build_query_params(
        self,
        params: Optional[QueryParams] = None,
        extra_query: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Build query parameters."""
        query_params = {}
        
        # Add custom query params
        query_params.update(self._custom_query)
        
        # Add request params
        if params:
            query_params.update(params)
        
        # Add extra query params
        if extra_query:
            query_params.update(extra_query)
        
        return query_params if query_params else None


class DefaultHttpxClient(BaseClient):
    """Synchronous HTTP client using httpx."""
    
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._client = self._build_client()
    
    def _build_client(self) -> httpx.Client:
        """Build the httpx client."""
        kwargs = {
            "timeout": self.timeout,
            "limits": DEFAULT_CONNECTION_LIMITS,
            "verify": self._verify,
        }
        
        if self._proxies is not None:
            kwargs["proxies"] = self._proxies
        
        if self._transport:
            kwargs["transport"] = self._transport
        
        return httpx.Client(**kwargs)
    
    def request(
        self,
        method: str,
        path: str,
        *,
        cast_to: Type[_T],
        body: Optional[Any] = None,
        params: Optional[QueryParams] = None,
        options: Optional[RequestOptions] = None,
    ) -> _T:
        """Make an HTTP request."""
        options = options or {}
        
        headers = self._build_headers(options.get("extra_headers"))
        query_params = self._build_query_params(params, options.get("extra_query"))
        url = self._build_url(path)
        
        # Prepare request body
        json_data = None
        if body is not None:
            if isinstance(body, (dict, list)):
                json_data = body
            elif hasattr(body, "model_dump"):
                json_data = body.model_dump()
            else:
                json_data = body
        
        # Handle timeout override
        timeout = options.get("timeout")
        if timeout is not None:
            timeout = httpx.Timeout(timeout)
        else:
            timeout = self.timeout
        
        # Make the request with retries
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=query_params,
                    json=json_data,
                    timeout=timeout,
                )
                
                # Check for HTTP errors
                if response.status_code >= 400:
                    raise make_status_error_from_response(response)
                
                # Parse and return the response
                return self._parse_response(response, cast_to=cast_to)
                
            except httpx.TimeoutException as e:
                last_exception = APITimeoutError(request=e.request)
                if attempt == self.max_retries:
                    raise last_exception
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except httpx.ConnectError as e:
                last_exception = APIConnectionError(request=e.request)
                if attempt == self.max_retries:
                    raise last_exception
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                if attempt == self.max_retries:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        
        # This should never be reached, but just in case
        if last_exception:
            raise last_exception
        raise APIError("Request failed after retries")
    
    def _parse_response(self, response: httpx.Response, *, cast_to: Type[_T]) -> _T:
        """Parse an HTTP response."""
        try:
            json_data = response.json()
        except Exception:
            raise APIError(f"Failed to parse response as JSON: {response.text}")
        
        if hasattr(cast_to, "model_validate"):
            return cast_to.model_validate(json_data)
        else:
            return json_data
    
    def with_raw_response(
        self,
        method: str,
        path: str,
        *,
        cast_to: Type[_T],
        body: Optional[Any] = None,
        params: Optional[QueryParams] = None,
        options: Optional[RequestOptions] = None,
    ) -> APIResponse[_T]:
        """Make a request and return the raw response."""
        options = options or {}
        
        headers = self._build_headers(options.get("extra_headers"))
        query_params = self._build_query_params(params, options.get("extra_query"))
        url = self._build_url(path)
        
        # Prepare request body
        json_data = None
        if body is not None:
            if isinstance(body, (dict, list)):
                json_data = body
            elif hasattr(body, "model_dump"):
                json_data = body.model_dump()
            else:
                json_data = body
        
        # Handle timeout override
        timeout = options.get("timeout")
        if timeout is not None:
            timeout = httpx.Timeout(timeout)
        else:
            timeout = self.timeout
        
        response = self._client.request(
            method=method,
            url=url,
            headers=headers,
            params=query_params,
            json=json_data,
            timeout=timeout,
        )
        
        return APIResponse(response, cast_to=cast_to)
    
    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DefaultAsyncHttpxClient(BaseClient):
    """Asynchronous HTTP client using httpx."""
    
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._client = self._build_client()
    
    def _build_client(self) -> httpx.AsyncClient:
        """Build the httpx async client."""
        kwargs = {
            "timeout": self.timeout,
            "limits": DEFAULT_CONNECTION_LIMITS,
            "verify": self._verify,
        }
        
        if self._proxies is not None:
            kwargs["proxies"] = self._proxies
        
        if self._transport:
            kwargs["transport"] = self._transport
        
        return httpx.AsyncClient(**kwargs)
    
    async def request(
        self,
        method: str,
        path: str,
        *,
        cast_to: Type[_T],
        body: Optional[Any] = None,
        params: Optional[QueryParams] = None,
        options: Optional[RequestOptions] = None,
    ) -> _T:
        """Make an async HTTP request."""
        options = options or {}
        
        headers = self._build_headers(options.get("extra_headers"))
        query_params = self._build_query_params(params, options.get("extra_query"))
        url = self._build_url(path)
        
        # Prepare request body
        json_data = None
        if body is not None:
            if isinstance(body, (dict, list)):
                json_data = body
            elif hasattr(body, "model_dump"):
                json_data = body.model_dump()
            else:
                json_data = body
        
        # Handle timeout override
        timeout = options.get("timeout")
        if timeout is not None:
            timeout = httpx.Timeout(timeout)
        else:
            timeout = self.timeout
        
        # Make the request with retries
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=query_params,
                    json=json_data,
                    timeout=timeout,
                )
                
                # Check for HTTP errors
                if response.status_code >= 400:
                    raise make_status_error_from_response(response)
                
                # Parse and return the response
                return await self._parse_response(response, cast_to=cast_to)
                
            except httpx.TimeoutException as e:
                last_exception = APITimeoutError(request=e.request)
                if attempt == self.max_retries:
                    raise last_exception
                await self._async_sleep(2 ** attempt)  # Exponential backoff
                
            except httpx.ConnectError as e:
                last_exception = APIConnectionError(request=e.request)
                if attempt == self.max_retries:
                    raise last_exception
                await self._async_sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                if attempt == self.max_retries:
                    raise
                await self._async_sleep(2 ** attempt)  # Exponential backoff
        
        # This should never be reached, but just in case
        if last_exception:
            raise last_exception
        raise APIError("Request failed after retries")
    
    async def _async_sleep(self, seconds: float) -> None:
        """Async sleep helper."""
        import asyncio
        await asyncio.sleep(seconds)
    
    async def _parse_response(self, response: httpx.Response, *, cast_to: Type[_T]) -> _T:
        """Parse an async HTTP response."""
        try:
            json_data = response.json()
        except Exception:
            raise APIError(f"Failed to parse response as JSON: {response.text}")
        
        if hasattr(cast_to, "model_validate"):
            return cast_to.model_validate(json_data)
        else:
            return json_data
    
    async def with_raw_response(
        self,
        method: str,
        path: str,
        *,
        cast_to: Type[_T],
        body: Optional[Any] = None,
        params: Optional[QueryParams] = None,
        options: Optional[RequestOptions] = None,
    ) -> AsyncAPIResponse[_T]:
        """Make an async request and return the raw response."""
        options = options or {}
        
        headers = self._build_headers(options.get("extra_headers"))
        query_params = self._build_query_params(params, options.get("extra_query"))
        url = self._build_url(path)
        
        # Prepare request body
        json_data = None
        if body is not None:
            if isinstance(body, (dict, list)):
                json_data = body
            elif hasattr(body, "model_dump"):
                json_data = body.model_dump()
            else:
                json_data = body
        
        # Handle timeout override
        timeout = options.get("timeout")
        if timeout is not None:
            timeout = httpx.Timeout(timeout)
        else:
            timeout = self.timeout
        
        response = await self._client.request(
            method=method,
            url=url,
            headers=headers,
            params=query_params,
            json=json_data,
            timeout=timeout,
        )
        
        return AsyncAPIResponse(response, cast_to=cast_to)
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()