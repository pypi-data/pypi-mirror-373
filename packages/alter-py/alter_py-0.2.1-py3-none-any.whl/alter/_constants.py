"""Constants for the Alter Python client."""

import httpx

# Default timeout for API requests (60 seconds)
DEFAULT_TIMEOUT = httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0)

# Default maximum number of retries
DEFAULT_MAX_RETRIES = 2

# Default connection limits
DEFAULT_CONNECTION_LIMITS = httpx.Limits(
    max_keepalive_connections=20,
    max_connections=100,
    keepalive_expiry=30.0,
)

# API version
API_VERSION = "v1"

# User agent
USER_AGENT = "alter-py/0.1.0"

# Base URLs
DEFAULT_BASE_URL = "http://localhost:8000/api/v1"  # For development
# Production: "https://api.alter.ai/api/v1"