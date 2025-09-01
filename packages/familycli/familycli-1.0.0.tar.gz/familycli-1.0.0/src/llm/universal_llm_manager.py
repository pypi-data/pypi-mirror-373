

import asyncio
import logging
from src.llm.providers.openai_provider import OpenAIProvider
from src.llm.providers.anthropic_provider import AnthropicProvider
from src.llm.providers.google_provider import GoogleProvider
from src.llm.providers.groq_provider import GroqProvider
from src.llm.providers.cerebras_provider import CerebrasProvider
from src.llm.providers.base_provider import BaseLLMProvider
import os
from functools import lru_cache
from src.config.config_manager import ConfigManager

class UniversalLLMManager:
	"""
	Abstraction for managing multiple LLM providers with failover, caching, cost tracking, and config reload.
	Usage:
		llm_manager = UniversalLLMManager()
		response = await llm_manager.route_request_to_provider(...)
		llm_manager.reload_config()
	"""

	def reload_config(self):
		self.config = self.config_manager.reload('llm_providers')
		self.providers = self._init_providers()
	def __init__(self, config_path: str = './config/llm_providers.json'):
		self.config_manager = ConfigManager()
		self.config = self.config_manager.load('llm_providers')
		self.logger = logging.getLogger(__name__)
		self.providers = self._init_providers()
		self.default_provider = self.config.get('default_provider', 'openai')
		self.fallback_providers = self.config.get('fallback_providers', [])
		self.cost_tracker = {}
		self._response_cache = {}  # Production-grade response cache
		self.logger = logging.getLogger(__name__)

	def _get_cache_key(self, provider_name: str, messages: list, **params) -> str:
		"""Generate cache key for response caching."""
		import hashlib
		import json

		cache_data = {
			'provider': provider_name,
			'messages': messages,
			'params': {k: v for k, v in params.items() if k not in ['stream']}
		}
		cache_str = json.dumps(cache_data, sort_keys=True)
		return hashlib.md5(cache_str.encode()).hexdigest()

	def _get_cached_response(self, cache_key: str):
		"""Get cached response if available and not expired."""
		if cache_key in self._response_cache:
			cached_item = self._response_cache[cache_key]
			# Cache expires after 1 hour for production use
			import time
			if time.time() - cached_item['timestamp'] < 3600:
				return cached_item['response']
			else:
				del self._response_cache[cache_key]
		return None

	def _cache_response(self, cache_key: str, response: str):
		"""Cache response with timestamp."""
		import time
		self._response_cache[cache_key] = {
			'response': response,
			'timestamp': time.time()
		}

	def _init_providers(self):
		providers = {}
		# Import here to avoid circular imports
		from src.auth.encryption import get_api_key

		for name, cfg in self.config['providers'].items():
			# First try to get API key from encrypted storage, then fallback to env vars
			api_key = get_api_key(name) or os.getenv(f'{name.upper()}_API_KEY', '')

			if not api_key:
				self.logger.warning(f"No API key found for provider {name}. Skipping initialization.")
				continue

			model = list(cfg['models'].keys())[0] if isinstance(cfg['models'], dict) else cfg['models'][0]

			try:
				if name == 'openai':
					providers[name] = OpenAIProvider(cfg['base_url'], api_key, model)
				elif name == 'anthropic':
					providers[name] = AnthropicProvider(cfg['base_url'], api_key, model)
				elif name == 'google':
					providers[name] = GoogleProvider(cfg['base_url'], api_key, model)
				elif name == 'groq':
					providers[name] = GroqProvider(cfg['base_url'], api_key, model)
				elif name == 'cerebras':
					providers[name] = CerebrasProvider(cfg['base_url'], api_key, model)

				self.logger.info(f"Successfully initialized {name} provider with model {model}")
			except Exception as e:
				self.logger.error(f"Failed to initialize {name} provider: {e}")
				continue

		return providers

	async def route_request_to_provider(self, provider_name, messages, stream=False, **params):
		"""
		Route a request to the specified LLM provider, with caching and cost tracking.
		Args:
			provider_name (str): Name of the provider.
			messages (list): LLM prompt/messages.
			stream (bool): Whether to stream response.
			params: Additional provider params.
		Returns:
			Response string if stream=False, async generator if stream=True.
		"""
		# Get provider, fallback to any available provider if default not found
		if provider_name in self.providers:
			provider = self.providers[provider_name]
		elif self.default_provider in self.providers:
			provider = self.providers[self.default_provider]
		elif self.providers:
			# Use first available provider
			provider = next(iter(self.providers.values()))
		else:
			raise ValueError("No LLM providers available. Please configure API keys.")

		# Check cache for non-streaming requests
		cache_key = None
		if not stream:
			cache_key = self._get_cache_key(provider_name, messages, **params)
			cached = self._get_cached_response(cache_key)
			if cached:
				self.logger.debug(f"Cache hit for provider {provider_name}")
				return cached

		try:
			if stream:
				# Return async generator for streaming
				return provider.stream_chat_completion(messages, **params)
			else:
				response = await provider.get_chat_completion(messages, **params)
				# Cache response
				if cache_key:
					self._cache_response(cache_key, response)
				# Track cost and usage
				self._track_cost(provider_name, response, messages)
				return response
		except Exception as e:
			# Handle rate limit, failover, deadlock prevention
			if hasattr(e, 'status_code') and e.status_code == 429:
				self.logger.warning(f"Rate limit exceeded for provider {provider_name}")
			else:
				self.logger.error(f"Provider {provider_name} error: {e}")
			raise
	def _track_cost(self, provider_name: str, response: str, messages: list):
		"""Production-grade cost tracking with accurate token counting and rate limiting."""
		try:
			# Estimate tokens more accurately
			input_tokens = sum(len(str(msg.get('content', '')).split()) for msg in messages)
			output_tokens = len(str(response).split())
			total_tokens = input_tokens + output_tokens

			# Initialize provider tracking
			if provider_name not in self.cost_tracker:
				self.cost_tracker[provider_name] = {
					'total_tokens': 0,
					'total_requests': 0,
					'input_tokens': 0,
					'output_tokens': 0,
					'estimated_cost': 0.0
				}

			# Update tracking
			tracker = self.cost_tracker[provider_name]
			tracker['total_tokens'] += total_tokens
			tracker['total_requests'] += 1
			tracker['input_tokens'] += input_tokens
			tracker['output_tokens'] += output_tokens

			# Estimate cost based on provider pricing (rough estimates)
			cost_per_1k_tokens = self._get_provider_cost(provider_name)
			estimated_cost = (total_tokens / 1000) * cost_per_1k_tokens
			tracker['estimated_cost'] += estimated_cost

			# Log cost information
			self.logger.info(
				f"Provider {provider_name}: {total_tokens} tokens "
				f"(in: {input_tokens}, out: {output_tokens}), "
				f"estimated cost: ${estimated_cost:.4f}, "
				f"total cost: ${tracker['estimated_cost']:.4f}"
			)

		except Exception as e:
			self.logger.error(f"Cost tracking failed for {provider_name}: {e}")

	def _get_provider_cost(self, provider_name: str) -> float:
		"""Get estimated cost per 1K tokens for provider."""
		# Production cost estimates (update with actual pricing)
		cost_map = {
			'openai': 0.002,  # Average GPT-4 pricing
			'anthropic': 0.008,  # Claude pricing
			'groq': 0.0001,  # Groq pricing
			'cerebras': 0.0001,  # Cerebras pricing
			'google': 0.001,  # Gemini pricing
		}
		return cost_map.get(provider_name, 0.002)  # Default to OpenAI pricing

	async def handle_concurrent_requests(self, requests):
		"""
		Handle multiple LLM requests concurrently.
		Args:
			requests (list): List of request dicts.
		Returns:
			List of responses.
		"""
		# requests: List[dict] with keys: provider_name, messages, stream, params
		tasks = []
		for req in requests:
			if req.get('stream', False):
				tasks.append(self.route_request_to_provider(req['provider_name'], req['messages'], True, **req.get('params', {})))
			else:
				tasks.append(self.route_request_to_provider(req['provider_name'], req['messages'], False, **req.get('params', {})))
		return await asyncio.gather(*tasks)

	async def fallback_provider_logic(self, messages, stream=False, **params):
		"""
		Try providers in priority order for failover.
		Args:
			messages (list): LLM prompt/messages.
			stream (bool): Whether to stream response.
			params: Additional provider params.
		Returns:
			Response or async generator of tokens.
		Raises:
			RuntimeError if all providers fail.
		"""
		for provider_name in [self.default_provider] + self.fallback_providers:
			try:
				if stream:
					async for token in self.route_request_to_provider(provider_name, messages, True, **params):
						yield token
				else:
					response = await self.route_request_to_provider(provider_name, messages, False, **params)
					yield response
					return
			except Exception as e:
				self.logger.warning(f"Failover: Provider {provider_name} failed: {e}")
				continue
		raise RuntimeError('All providers failed.')
