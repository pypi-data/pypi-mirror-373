"""Type definitions for the Alter Python client."""

import sys
from typing import Any, Dict, List, Mapping, Optional, TypeVar, Union
from typing_extensions import Literal, Required, TypedDict, NotRequired

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

# Custom types
NoneType = type(None)

# Transport and proxy types  
ProxiesTypes = Optional[Dict[str, Optional[str]]]

class Transport(Protocol):
    def handle_request(self, request: Any) -> Any:
        ...

# Request options
class RequestOptions(TypedDict, total=False):
    timeout: NotRequired[float]
    max_retries: NotRequired[int]
    extra_headers: NotRequired[Dict[str, str]]
    extra_query: NotRequired[Dict[str, Any]]
    extra_body: NotRequired[Dict[str, Any]]

# Generic type for omitted values
_T = TypeVar("_T")

class NotGiven:
    """
    A sentinel singleton class used to distinguish 'None' from 'not given' for
    distinguishing between explicit 'None' values and unset values.
    """
    
    def __bool__(self) -> Literal[False]:
        return False
    
    def __repr__(self) -> str:
        return "NOT_GIVEN"

NOT_GIVEN = NotGiven()

# Utility type for omitting values
def Omit() -> Any:
    return NOT_GIVEN

# Query parameters type
QueryParams = Dict[str, Union[str, int, float, bool, List[Any], None]]

# Headers type
Headers = Dict[str, str]

# Request body type
Body = Union[str, bytes, Dict[str, Any], None]

# JSON serializable types
JSONSerializable = Union[
    str,
    int,
    float,
    bool,
    None,
    Dict[str, "JSONSerializable"],
    List["JSONSerializable"],
]