
import aiohttp
from typing import Dict, Any

class APIHandler:
	def __init__(self, base_url: str, headers: Dict[str, str]):
		self.base_url = base_url
		self.headers = headers

	async def post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
		url = f"{self.base_url}/{endpoint}"
		async with aiohttp.ClientSession() as session:
			async with session.post(url, headers=self.headers, json=payload) as resp:
				if resp.status != 200:
					raise Exception(f"API request failed: {resp.status}")
				return await resp.json()
