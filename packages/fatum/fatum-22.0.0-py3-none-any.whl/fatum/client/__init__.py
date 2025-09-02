"""Generic Request Pattern implementation for type-safe API clients."""

from fatum.client.base import BaseClient
from fatum.client.errors import (
    ClientError,
    ConfigurationError,
    PermanentError,
    RetryableError,
)
from fatum.client.types import (
    ClientConfig,
    EmptyRequest,
    EndpointConfig,
    RetryConfig,
)

__all__ = [
    "BaseClient",
    "ClientConfig",
    "EmptyRequest",
    "EndpointConfig",
    "RetryConfig",
    "ClientError",
    "ConfigurationError",
    "PermanentError",
    "RetryableError",
]
