"""Base model classes for the Alter Python client."""

import json
import inspect
from typing import Any, Dict, Optional, Type, TypeVar, Union, cast
from typing_extensions import override
from pydantic import BaseModel as _BaseModel, ConfigDict

__all__ = ["BaseModel"]

_T = TypeVar("_T", bound="BaseModel")


class BaseModel(_BaseModel):
    """Base model for all Alter API response objects."""
    
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.model_dump_json()})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.model_dump()})"
    
    @override
    def model_dump(
        self,
        *,
        mode: str = "python",
        include: Optional[Any] = None,
        exclude: Optional[Any] = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> Dict[str, Any]:
        """Override model_dump to handle special cases."""
        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )
    
    @override
    def model_dump_json(
        self,
        *,
        indent: Optional[Union[int, str]] = None,
        include: Optional[Any] = None,
        exclude: Optional[Any] = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> str:
        """Override model_dump_json to handle special cases."""
        return super().model_dump_json(
            indent=indent,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Convert the model to a JSON string."""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls: Type[_T], data: Dict[str, Any]) -> _T:
        """Create a model instance from a dictionary."""
        return cls.model_validate(data)
    
    @classmethod
    def from_json(cls: Type[_T], json_str: str) -> _T:
        """Create a model instance from a JSON string."""
        return cls.model_validate_json(json_str)