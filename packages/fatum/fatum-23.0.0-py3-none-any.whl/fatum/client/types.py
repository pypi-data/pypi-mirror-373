"""Type definitions for the generic client pattern."""

from __future__ import annotations

from collections.abc import AsyncIterable, Iterable
from typing import Any, Generic, Literal, Mapping, TypeVar

from pydantic import BaseModel, ConfigDict, Field

RequestT = TypeVar("RequestT", bound=BaseModel)
ResponseT = TypeVar("ResponseT", bound=BaseModel)
ConfigT = TypeVar("ConfigT", bound="ClientConfig")

HTTPMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
StatusCode = int
Headers = Mapping[str, str]
RequestID = str | None
ResponseBody = str | bytes | None

FilesParam = Mapping[str, Any]
StreamContent = bytes | str | Iterable[bytes] | AsyncIterable[bytes]


class RetryConfig(BaseModel):
    """Configuration for retry behavior.

    This class defines how retries should be performed for failed requests.
    Setting max_attempts to 0 disables retries entirely.

    Attributes
    ----------
    max_attempts : int
        Maximum number of retry attempts (0 = no retries, default: 3).
    min_wait : float
        Minimum wait time in seconds between retries (default: 1.0).
    max_wait : float
        Maximum wait time in seconds between retries (default: 10.0).
    multiplier : float
        Exponential backoff multiplier (default: 2.0).
    retry_on_status : frozenset[int]
        HTTP status codes that trigger retries (default: 408, 429, 502, 503, 504).
    retry_on_exceptions : tuple[type[Exception], ...]
        Exception types that trigger retries (default: empty).

    Examples
    --------
    >>> # Disable retries
    >>> no_retry = RetryConfig(max_attempts=0)
    >>>
    >>> # Aggressive retry for critical endpoint
    >>> aggressive = RetryConfig(
    ...     max_attempts=5,
    ...     min_wait=0.5,
    ...     max_wait=30.0,
    ...     multiplier=1.5
    ... )
    >>>
    >>> # Custom retry conditions
    >>> custom = RetryConfig(
    ...     max_attempts=3,
    ...     retry_on_status=frozenset({429, 503}),
    ...     retry_on_exceptions=(TimeoutError,)
    ... )
    """

    model_config = ConfigDict(frozen=True)

    max_attempts: int = Field(default=3, ge=0, le=10)
    min_wait: float = Field(default=1.0, ge=0.0, le=60.0)
    max_wait: float = Field(default=10.0, ge=0.0, le=300.0)
    multiplier: float = Field(default=2.0, ge=1.0, le=10.0)
    retry_on_status: frozenset[int] = Field(default_factory=lambda: frozenset({408, 429, 502, 503, 504}))
    retry_on_exceptions: tuple[type[Exception], ...] = Field(default_factory=tuple)


class EmptyRequest(BaseModel):
    """Canonical empty request for endpoints with no request body.

    Use this for GET, DELETE, HEAD endpoints that don't accept request data.
    This ensures type consistency across the Generic Request Pattern.

    Examples
    --------
    >>> GET_ENDPOINT = EndpointConfig[EmptyRequest, UserResponse](
    ...     path="/users/{id}",
    ...     method="GET",
    ...     request_type=EmptyRequest,
    ...     response_type=UserResponse,
    ... )
    """

    model_config = ConfigDict(frozen=True, extra="forbid")


class EndpointConfig(BaseModel, Generic[RequestT, ResponseT]):
    """Configuration for a type-safe API endpoint.

    This class encapsulates all the information needed to make a request to an endpoint
    while preserving full type information. The generic parameters ensure that the
    request and response types flow through to the client methods.

    Parameters
    ----------
    RequestT : type[BaseModel]
        The type of the request data model.
    ResponseT : type[BaseModel]
        The type of the response data model.

    Attributes
    ----------
    path : str
        The URL path for the endpoint (relative to base_url).
    request_type : type[RequestT]
        The Pydantic model class for request validation.
    response_type : type[ResponseT]
        The Pydantic model class for response validation.
    method : HTTPMethod
        The HTTP method to use for this endpoint (default: "POST").
    retry_config : RetryConfig | None
        Override retry configuration for this specific endpoint (default: None).
        If None, uses the client's default retry configuration.
        Set to RetryConfig(max_attempts=0) to disable retries for this endpoint.

    Examples
    --------
    >>> from pydantic import BaseModel
    >>> class GenerationRequest(BaseModel):
    ...     prompt: str
    ...     max_tokens: int
    >>> class GenerationResponse(BaseModel):
    ...     text: str
    ...     tokens_used: int
    >>>
    >>> # Standard endpoint using client defaults
    >>> GENERATION_ENDPOINT = EndpointConfig[GenerationRequest, GenerationResponse](
    ...     path="/api/v1/generation",
    ...     method="POST",
    ...     request_type=GenerationRequest,
    ...     response_type=GenerationResponse,
    ... )
    >>>
    >>> # Critical endpoint with aggressive retries
    >>> CRITICAL_ENDPOINT = EndpointConfig[GenerationRequest, GenerationResponse](
    ...     path="/api/v1/critical",
    ...     request_type=GenerationRequest,
    ...     response_type=GenerationResponse,
    ...     retry_config=RetryConfig(max_attempts=5, max_wait=30.0)
    ... )
    >>>
    >>> # Fast-fail endpoint with no retries
    >>> FAST_FAIL_ENDPOINT = EndpointConfig[GenerationRequest, GenerationResponse](
    ...     path="/api/v1/fast",
    ...     request_type=GenerationRequest,
    ...     response_type=GenerationResponse,
    ...     retry_config=RetryConfig(max_attempts=0)
    ... )

    Notes
    -----
    The configuration is frozen (immutable) to prevent accidental modification
    after initialization.
    """

    model_config = ConfigDict(frozen=True)

    path: str
    request_type: type[RequestT]
    response_type: type[ResponseT]
    method: HTTPMethod = "POST"
    retry_config: RetryConfig | None = None


class ClientConfig(BaseModel):
    """Base configuration for API clients.

    All client configurations should inherit from this class to provide
    common settings required for HTTP communication. Subclasses can add
    API-specific configuration like API keys, custom headers, etc.

    Attributes
    ----------
    timeout : float
        Default timeout in seconds for requests (default: 30.0).
    connect_timeout : float
        Timeout in seconds for establishing connections (default: 5.0).
    max_retries : int
        Maximum number of retry attempts for failed requests (default: 3).
        DEPRECATED: Use retry_config.max_attempts instead.
    max_keepalive_connections : int
        Maximum number of keepalive connections to maintain (default: 5).
    max_connections : int
        Maximum total number of connections (default: 10).
    headers : Mapping[str, str]
        Default headers to include in all requests (default: empty dict).
    retry_config : RetryConfig | None
        Retry configuration for failed requests (default: RetryConfig()).
        Set to None or RetryConfig(max_attempts=0) to disable retries.

    Examples
    --------
    >>> # Default configuration with standard retries
    >>> config = MyAPIConfig()
    >>> client = MyAPIClient(config, base_url="https://api.example.com")
    >>>
    >>> # Disable retries globally
    >>> config = MyAPIConfig(
    ...     retry_config=RetryConfig(max_attempts=0)
    ... )
    >>> client = MyAPIClient(config, base_url="https://api.example.com")
    >>>
    >>> # Custom retry behavior
    >>> config = MyAPIConfig(
    ...     retry_config=RetryConfig(
    ...         max_attempts=5,
    ...         max_wait=30.0,
    ...         retry_on_status=frozenset({429, 503})
    ...     )
    ... )
    >>> client = MyAPIClient(config, base_url="https://api.example.com")

    Notes
    -----
    The configuration is frozen (immutable) to prevent accidental modification
    after initialization. This ensures thread-safety and prevents configuration
    drift during runtime.
    """

    model_config = ConfigDict(frozen=True)

    timeout: float = 30.0
    connect_timeout: float = 5.0
    max_keepalive_connections: int = 5
    max_connections: int = 10
    headers: Headers = Field(default_factory=dict)
    retry_config: RetryConfig | None = Field(default_factory=RetryConfig)
