"""Generic Request Pattern implementation for type-safe API clients.

This module implements the Generic Request Pattern (also known as the Type-Safe Client
Pattern or Parametric API Pattern). This is NOT a classic Gang of Four design pattern,
but rather a modern pattern that emerged from the intersection of functional programming
and advanced type systems.

Pattern Overview
----------------
The Generic Request Pattern uses parametric polymorphism to create a single,
reusable request method that maintains full type safety across different API
endpoints. Instead of writing separate methods for each endpoint (leading to
massive code duplication), we define endpoints as data using EndpointConfig
with generic type parameters.

How It Works
------------
1. EndpointConfig[RequestT, ResponseT] carries type information as data
2. A single _request() method handles all endpoints generically
3. Type parameters flow through, ensuring compile-time type safety
4. Subclasses just define endpoints and thin wrapper methods

Key Concepts
------------
- **Parametric Polymorphism**: One implementation, many types
- **Type Erasure**: Types exist at compile-time, erased at runtime
- **Higher-Kinded Types**: EndpointConfig is parameterized by type constructors
- **Bounded Quantification**: TypeVars bounded by BaseModel

Constants
---------
RETRYABLE_STATUS_CODES : frozenset[int]
    HTTP status codes that trigger automatic retry.
PERMANENT_ERROR_STATUS_CODES : frozenset[int]
    HTTP status codes that should not be retried.

Examples
--------
>>> from pydantic import BaseModel
>>> from fatum.client import BaseClient, EndpointConfig, ClientConfig
>>>
>>> class MyRequest(BaseModel):
...     query: str
>>>
>>> class MyResponse(BaseModel):
...     result: str
>>>
>>> class MyConfig(ClientConfig):
...     api_key: str
>>>
>>> class MyClient(BaseClient[MyConfig]):
...     ENDPOINT = EndpointConfig[MyRequest, MyResponse](
...         path="/api/endpoint",
...         request_type=MyRequest,
...         response_type=MyResponse,
...     )
...
...     async def my_method(self, req: MyRequest) -> MyResponse:
...         return await self._request(self.ENDPOINT, req)
>>>
>>> async with MyClient(config) as client:
...     response = await client.my_method(request)

Notes
-----
If this is too simple, just copy OpenAI's base client LOL!
"""

from __future__ import annotations

import asyncio
import json
import logging
from abc import ABC
from contextlib import suppress
from typing import Any, Generic, Self

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from fatum.client.errors import (
    ClientError,
    PermanentError,
    RetryableError,
)
from fatum.client.types import (
    ConfigT,
    EndpointConfig,
    FilesParam,
    Headers,
    RequestID,
    RequestT,
    ResponseT,
    StatusCode,
    StreamContent,
)

logger = logging.getLogger(__name__)

SUCCESS_STATUS_CODES = frozenset({200, 201, 204})
RETRYABLE_STATUS_CODES = frozenset({408, 429, 502, 503, 504})
PERMANENT_ERROR_STATUS_CODES = frozenset({400, 401, 403, 404, 405, 406, 409, 410, 422})


class BaseClient(ABC, Generic[ConfigT]):
    """Abstract base client for building type-safe API clients.

    This class implements the Generic Request Pattern, providing a reusable
    foundation for API clients with automatic retry logic, error handling,
    and full type safety.

    Parameters
    ----------
    config : ConfigT
        Configuration object containing API settings.

    Attributes
    ----------
    config : ConfigT
        The configuration object passed during initialization.
    _client : httpx.AsyncClient | None
        Lazy-initialized HTTP client instance.
    _is_closed : bool
        Flag indicating whether the client has been closed.

    Examples
    --------
    >>> class MyAPIConfig(ClientConfig):
    ...     api_key: str
    >>>
    >>> class MyAPIClient(BaseClient[MyAPIConfig]):
    ...     ENDPOINT = EndpointConfig[RequestType, ResponseType](
    ...         path="/api/endpoint",
    ...         request_type=RequestType,
    ...         response_type=ResponseType,
    ...     )
    ...
    ...     async def call_api(self, request: RequestType) -> ResponseType:
    ...         return await self._request(self.ENDPOINT, request)
    >>>
    >>> async with MyAPIClient(config) as client:
    ...     result = await client.call_api(request)

    Notes
    -----
    The client uses lazy initialization for the HTTP client to avoid
    creating resources until they're actually needed. Always use the
    client as an async context manager or explicitly call close().
    """

    def __init__(self, config: ConfigT) -> None:
        self.config = config
        self._client: httpx.AsyncClient | None = None
        self._is_closed = False

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client.

        Implements lazy initialization of the httpx client to avoid creating
        resources until they're needed.

        Returns
        -------
        httpx.AsyncClient
            The initialized HTTP client instance.

        Raises
        ------
        ClientError
            If the client has been closed.

        Notes
        -----
        The client is configured with settings from the config object,
        including timeouts, connection limits, and base URL.
        """
        if self._is_closed:
            raise ClientError("Client has been closed")

        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=httpx.Timeout(self.config.timeout, connect=self.config.connect_timeout),
                limits=httpx.Limits(
                    max_keepalive_connections=self.config.max_keepalive_connections,
                    max_connections=self.config.max_connections,
                ),
            )

        return self._client

    def _should_retry(self, status_code: StatusCode) -> bool:
        """Determine if a status code indicates a retryable error.

        Parameters
        ----------
        status_code : int
            The HTTP status code to check.

        Returns
        -------
        bool
            True if the error should be retried, False otherwise.

        Notes
        -----
        Following industry best practices (OpenAI, Anthropic, AWS), we retry on:
        - 408: Request Timeout
        - 429: Too Many Requests (rate limiting)
        - 502: Bad Gateway
        - 503: Service Unavailable
        - 504: Gateway Timeout
        """
        return status_code in RETRYABLE_STATUS_CODES

    def _classify_error(
        self,
        status_code: StatusCode,
        response_text: str,
        request_id: RequestID = None,
    ) -> ClientError:
        """Classify an HTTP error as retryable or permanent.

        Uses pattern matching to determine the appropriate error type based on
        the HTTP status code.

        Parameters
        ----------
        status_code : int
            The HTTP status code from the response.
        response_text : str
            The raw response body text.
        request_id : str | None, optional
            Request ID from response headers if available (default: None).

        Returns
        -------
        ClientError
            An appropriate error subclass (RetryableError or PermanentError).

        Notes
        -----
        This method determines whether the client should retry the request
        with backoff or fail immediately. The classification follows industry
        best practices for API error handling.
        """
        match status_code:
            case code if code in RETRYABLE_STATUS_CODES:
                return RetryableError(
                    f"Retryable error: {status_code}",
                    status_code=status_code,
                    response_body=response_text,
                    request_id=request_id,
                )
            case code if code in PERMANENT_ERROR_STATUS_CODES:
                return PermanentError(
                    f"Permanent error: {status_code}",
                    status_code=status_code,
                    response_body=response_text,
                    request_id=request_id,
                )
            case _:
                return ClientError(
                    f"Unexpected error: {status_code}",
                    status_code=status_code,
                    response_body=response_text,
                    request_id=request_id,
                )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(RetryableError),
        reraise=True,
    )
    async def _request(
        self,
        endpoint: EndpointConfig[RequestT, ResponseT],
        request_data: RequestT | None = None,
        *,
        files: FilesParam | None = None,
        content: StreamContent | None = None,
        headers: Headers | None = None,
        **kwargs: Any,
    ) -> ResponseT:
        """Make a request to an endpoint with automatic retry and error handling.

        This is the core method that all API calls go through. It provides:
        request serialization, HTTP communication, error classification,
        automatic retry with exponential backoff, and response deserialization.

        Parameters
        ----------
        endpoint : EndpointConfig[RequestT, ResponseT]
            Endpoint configuration containing path, method, and types.
        request_data : RequestT | None, optional
            Request data model for POST/PUT/PATCH methods (default: None).
        files : Mapping[str, Any] | None, optional
            Files to upload as multipart/form-data (default: None).
        content : bytes | str | Iterable[bytes] | AsyncIterable[bytes] | None, optional
            Raw content for streaming or binary uploads (default: None).
        headers : Mapping[str, str] | None, optional
            Per-request headers to override/extend config headers (default: None).
        **kwargs : Any
            Additional request options passed to httpx.

        Returns
        -------
        ResponseT
            Deserialized and validated response object.

        Raises
        ------
        RetryableError
            For transient failures (will be automatically retried).
        PermanentError
            For non-retryable failures (e.g., authentication errors).
        ClientError
            For other errors (e.g., parsing failures).

        Examples
        --------
        >>> endpoint = EndpointConfig[MyRequest, MyResponse](
        ...     path="/api/v1/resource",
        ...     request_type=MyRequest,
        ...     response_type=MyResponse,
        ... )
        >>> response = await client._request(endpoint, request_data)

        Notes
        -----
        This method is decorated with @retry from tenacity, which handles
        automatic retry logic with exponential backoff for RetryableError.
        The retry behavior is configured to attempt up to 3 times with
        exponential backoff between 1 and 10 seconds.
        """
        url = endpoint.path
        method = endpoint.method.lower()

        request_kwargs: dict[str, Any] = kwargs.copy()

        if headers or self.config.headers:
            request_kwargs["headers"] = {**self.config.headers, **(headers or {})}

        # NOTE: precedence logic: files > content > json
        if files is not None:
            request_kwargs |= {"files": files}
            if request_data:
                request_kwargs |= {"data": request_data.model_dump(mode="json")}
        elif content is not None:
            request_kwargs |= {"content": content}
        elif request_data is not None:
            request_kwargs |= {"json": request_data.model_dump(by_alias=True, exclude_none=True)}

        try:
            client = self._get_client()
            response = await client.request(method, url, **request_kwargs)

            request_id = response.headers.get("x-request-id")

            match response.status_code:
                case code if code in SUCCESS_STATUS_CODES:
                    try:
                        response_data = response.json()
                        return endpoint.response_type.model_validate(response_data)
                    except (json.JSONDecodeError, Exception) as e:
                        logger.error(f"Failed to parse response: {e}")
                        raise ClientError(
                            f"Invalid response format: {str(e)}",
                            response_body=response.text,
                            request_id=request_id,
                        ) from e
                case _:
                    error = self._classify_error(
                        response.status_code,
                        response.text,
                        request_id,
                    )

                    match error:
                        case RetryableError():
                            logger.warning(f"Retryable error for {endpoint}: {response.status_code}")
                        case _:
                            logger.error(f"Permanent error for {endpoint}: {response.status_code}")

                    raise error

        except httpx.TimeoutException as e:
            logger.warning(f"Request timeout for {endpoint}: {e}")
            raise RetryableError(
                f"Request timed out for {endpoint}",
                response_body=str(e),
            ) from e
        except httpx.NetworkError as e:
            logger.warning(f"Network error for {endpoint}: {e}")
            raise RetryableError(
                f"Network error for {endpoint}",
                response_body=str(e),
            ) from e
        except httpx.HTTPError as e:
            logger.error(f"HTTP error for {endpoint}: {e}")
            raise ClientError(
                f"HTTP error for {endpoint}: {str(e)}",
                response_body=str(e),
            ) from e

    async def __aenter__(self) -> Self:
        """Async context manager entry.

        Returns
        -------
        Self
            The client instance for use in async with statements.

        Examples
        --------
        >>> async with MyAPIClient(config) as client:
        ...     response = await client.call_endpoint(request)
        """
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit.

        Parameters
        ----------
        *args : object
            Exception information (unused).

        Notes
        -----
        Ensures the HTTP client is properly closed when exiting the context.
        """
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client and cleanup resources.

        This method should be called when the client is no longer needed.
        After calling this method, the client cannot be used for further requests.

        Examples
        --------
        >>> client = MyAPIClient(config)
        >>> try:
        ...     response = await client.call_api(request)
        ... finally:
        ...     await client.close()

        Notes
        -----
        It's recommended to use the client as an async context manager
        instead of manually calling close(), as this ensures proper cleanup
        even if an exception occurs.
        """
        if self._client and not self._is_closed:
            await self._client.aclose()
            self._client = None
            self._is_closed = True

    def __del__(self) -> None:
        """Cleanup method called during garbage collection.

        Attempts to close the HTTP client if it wasn't properly closed.
        This is a safety mechanism and should not be relied upon for cleanup.

        Notes
        -----
        Always prefer using the client as an async context manager or
        explicitly calling close() rather than relying on __del__.
        """
        if self._client and not self._is_closed:
            with suppress(Exception):
                asyncio.get_event_loop().run_until_complete(self.close())
