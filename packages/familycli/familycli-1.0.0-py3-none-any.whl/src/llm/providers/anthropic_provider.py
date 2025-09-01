import aiohttp
import asyncio
from typing import List, Dict, Any, AsyncGenerator
from src.llm.providers.base_provider import BaseLLMProvider
from tenacity import retry, stop_after_attempt, wait_exponential
import json

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, base_url: str, api_key: str, model: str, **kwargs):
        super().__init__(base_url, api_key, model, **kwargs)
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_chat_completion(self, messages: List[Dict[str, Any]], **params) -> str:
        url = f"{self.base_url}/messages"
        # Convert OpenAI-style messages to Anthropic format
        anthropic_messages = []
        system_message = None
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        payload = {
            "model": self.model,
            "messages": anthropic_messages,
            "max_tokens": params.get("max_tokens", 1024),
            **{k: v for k, v in params.items() if k not in ["max_tokens"]}
        }
        
        if system_message:
            payload["system"] = system_message
            
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=payload) as resp:
                await self.handle_rate_limits(resp)
                if resp.status != 200:
                    raise Exception(f"Anthropic API error: {resp.status}")
                data = await resp.json()
                if not self.validate_response(data):
                    raise ValueError("Invalid response from Anthropic API")
                return data["content"][0]["text"]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def stream_chat_completion(self, messages: List[Dict[str, Any]], **params) -> AsyncGenerator[str, None]:
        url = f"{self.base_url}/messages"
        # Convert OpenAI-style messages to Anthropic format
        anthropic_messages = []
        system_message = None
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        payload = {
            "model": self.model,
            "messages": anthropic_messages,
            "max_tokens": params.get("max_tokens", 1024),
            "stream": True,
            **{k: v for k, v in params.items() if k not in ["max_tokens"]}
        }
        
        if system_message:
            payload["system"] = system_message
            
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=payload) as resp:
                await self.handle_rate_limits(resp)
                if resp.status != 200:
                    raise Exception(f"Anthropic API error: {resp.status}")
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
            and "content" in response
            and len(response["content"]) > 0
            and "text" in response["content"][0]
        )
