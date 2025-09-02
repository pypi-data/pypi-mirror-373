"""Response classes for the Alter Python client."""

import inspect
from typing import Any, Dict, Generic, Optional, TypeVar, Union, cast
from typing_extensions import override
import httpx

from ._models import BaseModel

_T = TypeVar("_T")


class APIResponse(Generic[_T]):
    """Wrapper around httpx.Response with additional functionality."""
    
    def __init__(
        self,
        raw: httpx.Response,
        *,
        parsed: Optional[_T] = None,
        cast_to: Optional[type] = None,
    ) -> None:
        self._raw_response = raw
        self._parsed = parsed
        self._cast_to = cast_to
    
    @property
    def http_response(self) -> httpx.Response:
        """The underlying httpx.Response object."""
        return self._raw_response
    
    @property
    def status_code(self) -> int:
        """The response status code."""
        return self._raw_response.status_code
    
    @property
    def headers(self) -> httpx.Headers:
        """The response headers.""" 
        return self._raw_response.headers
    
    @property
    def content(self) -> bytes:
        """The raw response content."""
        return self._raw_response.content
    
    @property
    def text(self) -> str:
        """The response content as text."""
        return self._raw_response.text
    
    def json(self) -> Any:
        """Parse the response content as JSON."""
        return self._raw_response.json()
    
    def parse(self) -> _T:
        """Parse the response into the expected type."""
        if self._parsed is not None:
            return self._parsed
        
        if self._cast_to is None:
            raise RuntimeError("Cannot parse response - no type specified")
        
        json_data = self.json()
        
        if inspect.isclass(self._cast_to) and issubclass(self._cast_to, BaseModel):
            self._parsed = self._cast_to.model_validate(json_data)
        else:
            self._parsed = cast(_T, json_data)
        
        return self._parsed
    
    def __repr__(self) -> str:
        return f"<APIResponse [{self.status_code}]>"


class AsyncAPIResponse(Generic[_T]):
    """Async wrapper around httpx.Response with additional functionality."""
    
    def __init__(
        self,
        raw: httpx.Response,
        *,
        parsed: Optional[_T] = None,
        cast_to: Optional[type] = None,
    ) -> None:
        self._raw_response = raw
        self._parsed = parsed
        self._cast_to = cast_to
    
    @property
    def http_response(self) -> httpx.Response:
        """The underlying httpx.Response object."""
        return self._raw_response
    
    @property
    def status_code(self) -> int:
        """The response status code."""
        return self._raw_response.status_code
    
    @property
    def headers(self) -> httpx.Headers:
        """The response headers."""
        return self._raw_response.headers
    
    @property
    def content(self) -> bytes:
        """The raw response content."""
        return self._raw_response.content
    
    @property
    def text(self) -> str:
        """The response content as text."""
        return self._raw_response.text
    
    async def json(self) -> Any:
        """Parse the response content as JSON."""
        return self._raw_response.json()
    
    async def parse(self) -> _T:
        """Parse the response into the expected type."""
        if self._parsed is not None:
            return self._parsed
        
        if self._cast_to is None:
            raise RuntimeError("Cannot parse response - no type specified")
        
        json_data = await self.json()
        
        if inspect.isclass(self._cast_to) and issubclass(self._cast_to, BaseModel):
            self._parsed = self._cast_to.model_validate(json_data)
        else:
            self._parsed = cast(_T, json_data)
        
        return self._parsed
    
    def __repr__(self) -> str:
        return f"<AsyncAPIResponse [{self.status_code}]>"