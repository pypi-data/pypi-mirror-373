
import aiohttp
import asyncio
from typing import AsyncGenerator, Dict, Any

class StreamingClient:
	def __init__(self, base_url: str, headers: Dict[str, str]):
		self.base_url = base_url
		self.headers = headers

	async def stream(self, endpoint: str, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
		url = f"{self.base_url}/{endpoint}"
		async with aiohttp.ClientSession() as session:
			async with session.post(url, headers=self.headers, json=payload) as resp:
				if resp.status != 200:
					raise Exception(f"Streaming failed: {resp.status}")
				async for line in resp.content:
					if line:
						try:
							data = line.decode('utf-8').strip()
							if data.startswith('data: '):
								data = data[6:]
							if data:
								yield data
						except Exception:
							continue
