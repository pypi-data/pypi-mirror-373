"""Health check type definitions."""

from typing import Any, Dict
from datetime import datetime

from .._models import BaseModel

__all__ = [
    "HealthResponse",
    "DetailedHealthResponse",
]


class HealthResponse(BaseModel):
    """Basic health check response."""
    status: str
    timestamp: datetime
    version: str
    service: str = "alter-api"


class DetailedHealthResponse(HealthResponse):
    """Detailed health check response."""
    database: Dict[str, Any]
    redis: Dict[str, Any]
    external_services: Dict[str, Any]
    system: Dict[str, Any]