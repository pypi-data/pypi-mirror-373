"""Generic client pattern for building type-safe API clients.

This package provides a production-ready base client following patterns from
major SDKs (OpenAI, Anthropic, AWS) but simplified per YAGNI principles.

The pattern eliminates 70-80% of boilerplate code while maintaining full
type safety and IDE support.

Example:
    from fatum.client import BaseClient, EndpointConfig, ClientConfig
    from pydantic import BaseModel

    class TranslateRequest(BaseModel):
        text: str
        source_lang: str
        target_lang: str

    class TranslateResponse(BaseModel):
        translated_text: str

    class TranslationConfig(ClientConfig):
        api_key: str

    class TranslationClient(BaseClient[TranslationConfig]):
        TRANSLATE = EndpointConfig[TranslateRequest, TranslateResponse](
            path="/translate",
            request_type=TranslateRequest,
            response_type=TranslateResponse,
        )

        async def translate(self, request: TranslateRequest) -> TranslateResponse:
            return await self._request(self.TRANSLATE, request)

    # Usage
    async with TranslationClient(config) as client:
        result = await client.translate(request)
"""

from fatum.client.base import BaseClient
from fatum.client.errors import (
    ClientError,
    ConfigurationError,
    PermanentError,
    RetryableError,
)
from fatum.client.types import ClientConfig, EndpointConfig

__all__ = [
    # Base client
    "BaseClient",
    # Configuration
    "ClientConfig",
    "EndpointConfig",
    # Errors
    "ClientError",
    "RetryableError",
    "PermanentError",
    "ConfigurationError",
]
