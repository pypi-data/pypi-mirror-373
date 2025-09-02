"""Generic Request Pattern implementation for type-safe API clients."""

from fatum.client.base import BaseClient
from fatum.client.errors import (
    ClientError,
    PermanentError,
    RetryableError,
)
from fatum.client.types import (
    EmptyRequest,
    EndpointConfig,
)

__all__ = [
    "BaseClient",
    "EmptyRequest",
    "EndpointConfig",
    "ClientError",
    "PermanentError",
    "RetryableError",
]
