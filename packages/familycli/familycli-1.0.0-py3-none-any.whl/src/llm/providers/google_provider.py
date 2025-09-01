import aiohttp
import asyncio
from typing import List, Dict, Any, AsyncGenerator
from src.llm.providers.base_provider import BaseLLMProvider
from tenacity import retry, stop_after_attempt, wait_exponential
import json

class GoogleProvider(BaseLLMProvider):
    def __init__(self, base_url: str, api_key: str, model: str, **kwargs):
        super().__init__(base_url, api_key, model, **kwargs)
        self.headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_chat_completion(self, messages: List[Dict[str, Any]], **params) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": params.get("max_tokens", 1024),
            **{k: v for k, v in params.items() if k not in ["max_tokens"]}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=payload) as resp:
                await self.handle_rate_limits(resp)
                if resp.status != 200:
                    raise Exception(f"Google API error: {resp.status}")
                data = await resp.json()
                if not self.validate_response(data):
                    raise ValueError("Invalid response from Google API")
                return data["choices"][0]["message"]["content"]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def stream_chat_completion(self, messages: List[Dict[str, Any]], **params) -> AsyncGenerator[str, None]:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": params.get("max_tokens", 1024),
            "stream": True,
            **{k: v for k, v in params.items() if k not in ["max_tokens"]}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=payload) as resp:
                await self.handle_rate_limits(resp)
                if resp.status != 200:
                    raise Exception(f"Google API error: {resp.status}")
                async for line in resp.content:
                    if line:
                        try:
                            decoded_line = line.decode('utf-8').strip()
                            if decoded_line.startswith('data: '):
                                data = decoded_line[6:]
                                if data == '[DONE]':
                                    break
                                yield data
                        except Exception:
                            continue

    async def handle_rate_limits(self, response):
        if response.status == 429:
            await asyncio.sleep(2)
            raise Exception("Rate limit exceeded")
        elif response.status >= 500:
            await asyncio.sleep(2)
            raise Exception("Server error")

    async def retry_with_backoff(self, func, *args, **kwargs):
        for attempt in range(3):
            try:
                return await func(*args, **kwargs)
            except Exception:
                await asyncio.sleep(2 ** attempt)
        raise Exception("Max retries exceeded")

    def validate_response(self, response: Any) -> bool:
        return (
            isinstance(response, dict)
            and "choices" in response
            and len(response["choices"]) > 0
            and "message" in response["choices"][0]
            and "content" in response["choices"][0]["message"]
        )
