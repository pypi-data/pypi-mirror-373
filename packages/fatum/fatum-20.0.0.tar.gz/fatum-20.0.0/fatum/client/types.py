"""Type definitions for the generic client pattern."""

from __future__ import annotations

from typing import Generic, Literal, Mapping, TypeVar

from pydantic import BaseModel, ConfigDict, Field

RequestT = TypeVar("RequestT", bound=BaseModel)
ResponseT = TypeVar("ResponseT", bound=BaseModel)
ConfigT = TypeVar("ConfigT", bound="ClientConfig")

HTTPMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
StatusCode = int
Headers = Mapping[str, str]
RequestID = str | None
ResponseBody = str | bytes | None


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

    Examples
    --------
    >>> from pydantic import BaseModel
    >>> class GenerationRequest(BaseModel):
    ...     prompt: str
    ...     max_tokens: int
    >>> class GenerationResponse(BaseModel):
    ...     text: str
    ...     tokens_used: int
    >>> GENERATION_ENDPOINT = EndpointConfig[GenerationRequest, GenerationResponse](
    ...     path="/api/v1/generation",
    ...     method="POST",
    ...     request_type=GenerationRequest,
    ...     response_type=GenerationResponse,
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


class ClientConfig(BaseModel):
    """Base configuration for API clients.

    All client configurations should inherit from this class to provide
    common settings required for HTTP communication. Subclasses can add
    API-specific configuration like API keys, custom headers, etc.

    Attributes
    ----------
    base_url : str
        The base URL for all API requests.
    timeout : float
        Default timeout in seconds for requests (default: 30.0).
    connect_timeout : float
        Timeout in seconds for establishing connections (default: 5.0).
    max_retries : int
        Maximum number of retry attempts for failed requests (default: 3).
    max_keepalive_connections : int
        Maximum number of keepalive connections to maintain (default: 5).
    max_connections : int
        Maximum total number of connections (default: 10).
    headers : Mapping[str, str]
        Default headers to include in all requests (default: empty dict).

    Examples
    --------
    >>> class MyAPIConfig(ClientConfig):
    ...     api_key: str
    ...     environment: Literal["dev", "prod"] = "prod"
    >>> config = MyAPIConfig(
    ...     base_url="https://api.example.com",
    ...     api_key="secret-key",
    ...     timeout=60.0,
    ... )

    Notes
    -----
    The configuration is frozen (immutable) to prevent accidental modification
    after initialization. This ensures thread-safety and prevents configuration
    drift during runtime.
    """

    model_config = ConfigDict(frozen=True)

    base_url: str
    timeout: float = 30.0
    connect_timeout: float = 5.0
    max_retries: int = 3
    max_keepalive_connections: int = 5
    max_connections: int = 10
    headers: Headers = Field(default_factory=dict)
