import abc
import asyncio
from typing import Any, Dict, Optional, AsyncGenerator

class BaseLLMProvider(abc.ABC):
    """
    Abstract base class for all LLM providers. Production-grade: all methods must be implemented by subclasses.
    """
    def __init__(self, base_url: str, api_key: str, model: str, **kwargs):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.config = kwargs

    @abc.abstractmethod
    async def stream_chat_completion(self, messages: list, **params) -> AsyncGenerator[str, None]:
        """
        Stream chat completion responses token-by-token.
        """
        pass

    @abc.abstractmethod
    async def get_chat_completion(self, messages: list, **params) -> str:
        """
        Get full chat completion response.
        """
        pass

    @abc.abstractmethod
    async def handle_rate_limits(self, response: Any) -> None:
        """
        Handle rate limits and retry logic.
        """
        pass

    @abc.abstractmethod
    async def retry_with_backoff(self, func, *args, **kwargs) -> Any:
        """
        Retry a function with exponential backoff.
        """
        pass

    @abc.abstractmethod
    def validate_response(self, response: Any) -> bool:
        """
        Validate the response from the LLM provider.
        """
        pass
