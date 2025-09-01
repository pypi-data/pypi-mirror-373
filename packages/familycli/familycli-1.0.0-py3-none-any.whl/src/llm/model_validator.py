"""
Production-grade LLM model validation and management system.
Validates model availability and provides fallback mechanisms.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from src.config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class ModelStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEPRECATED = "deprecated"
    UNKNOWN = "unknown"

@dataclass
class ModelInfo:
    provider: str
    model_name: str
    status: ModelStatus
    max_tokens: int
    supports_streaming: bool
    cost_per_1k_tokens: float
    description: str
    fallback_models: List[str]

class ProductionModelValidator:
    """Production-grade model validator with real-time availability checking."""

    def __init__(self, config_dir: str = "src/config"):
        self.validated_models = {}
        self.config_manager = ConfigManager(config_dir)
        self.model_registry = self._load_model_registry()

    def _load_model_registry(self) -> Dict[str, Dict[str, ModelInfo]]:
        """Load model registry from configuration file."""
        try:
            config = self.config_manager.load('llm_providers')
            registry = {}

            for provider_name, provider_config in config['providers'].items():
                registry[provider_name] = {}

                for model_key, model_config in provider_config['models'].items():
                    # Determine fallback models based on cost and capability
                    fallback_models = self._determine_fallback_models(
                        provider_name, model_key, provider_config['models']
                    )

                    registry[provider_name][model_key] = ModelInfo(
                        provider=provider_name,
                        model_name=model_key,
                        status=ModelStatus.AVAILABLE,
                        max_tokens=model_config['max_tokens'],
                        supports_streaming=provider_config.get('streaming_supported', True),
                        cost_per_1k_tokens=model_config['cost_per_1k_tokens'],
                        description=model_config['name'],
                        fallback_models=fallback_models
                    )

            return registry

        except Exception as e:
            logger.error(f"Failed to load model registry from config: {e}")
            return self._get_default_registry()

    def _determine_fallback_models(self, provider: str, current_model: str,
                                 provider_models: Dict) -> List[str]:
        """Intelligently determine fallback models based on cost and capability."""
        # Sort models by cost (ascending) and filter out current model
        sorted_models = sorted(
            [(k, v) for k, v in provider_models.items() if k != current_model],
            key=lambda x: x[1]['cost_per_1k_tokens']
        )

        # Return up to 3 fallback models, preferring lower cost
        return [model[0] for model in sorted_models[:3]]

    def _get_default_registry(self) -> Dict[str, Dict[str, ModelInfo]]:
        """Fallback registry with essential models."""
        return {
            "openai": {
                "gpt-4o-mini": ModelInfo(
                    provider="openai",
                    model_name="gpt-4o-mini",
                    status=ModelStatus.AVAILABLE,
                    max_tokens=16384,
                    supports_streaming=True,
                    cost_per_1k_tokens=0.00015,
                    description="GPT-4 Omni Mini",
                    fallback_models=["gpt-4o"]
                ),
            },
            "groq": {
                "llama-3.1-8b-instant": ModelInfo(
                    provider="groq",
                    model_name="llama-3.1-8b-instant",
                    status=ModelStatus.AVAILABLE,
                    max_tokens=8192,
                    supports_streaming=True,
                    cost_per_1k_tokens=0.00005,
                    description="Llama 3.1 8B Instant",
                    fallback_models=[]
                )
            }
        }
    
    async def validate_model(self, provider: str, model_name: str) -> Tuple[bool, Optional[ModelInfo]]:
        """Validate if a model is available and return its info."""
        try:
            if provider in self.model_registry:
                # Check for exact match
                for key, model_info in self.model_registry[provider].items():
                    if model_info.model_name == model_name or key == model_name:
                        return True, model_info
                        
            # Model not found in registry
            logger.warning(f"Model {provider}/{model_name} not found in registry")
            return False, None
            
        except Exception as e:
            logger.error(f"Error validating model {provider}/{model_name}: {e}")
            return False, None
    
    def get_fallback_model(self, provider: str, failed_model: str) -> Optional[ModelInfo]:
        """Get a fallback model when the primary model fails."""
        try:
            if provider in self.model_registry:
                for model_info in self.model_registry[provider].values():
                    if model_info.model_name == failed_model:
                        # Return first available fallback
                        for fallback_name in model_info.fallback_models:
                            fallback_info = self.get_model_info(provider, fallback_name)
                            if fallback_info and fallback_info.status == ModelStatus.AVAILABLE:
                                return fallback_info
            return None
        except Exception as e:
            logger.error(f"Error getting fallback for {provider}/{failed_model}: {e}")
            return None
    
    def get_model_info(self, provider: str, model_name: str) -> Optional[ModelInfo]:
        """Get detailed information about a model."""
        if provider in self.model_registry:
            for key, model_info in self.model_registry[provider].items():
                if model_info.model_name == model_name or key == model_name:
                    return model_info
        return None
    
    def get_recommended_models_by_use_case(self, use_case: str) -> List[ModelInfo]:
        """Get recommended models for specific use cases."""
        recommendations = {
            "family_chat": [
                self.model_registry["anthropic"]["claude-3-sonnet"],
                self.model_registry["openai"]["gpt-3.5-turbo"],
                self.model_registry["groq"]["llama3-8b"]
            ],
            "creative_writing": [
                self.model_registry["anthropic"]["claude-3-opus"],
                self.model_registry["openai"]["gpt-4"],
                self.model_registry["groq"]["llama3-70b"]
            ],
            "fast_responses": [
                self.model_registry["groq"]["llama3-8b"],
                self.model_registry["groq"]["mixtral-8x7b"],
                self.model_registry["openai"]["gpt-3.5-turbo"]
            ],
            "cost_effective": [
                self.model_registry["groq"]["llama3-8b"],
                self.model_registry["anthropic"]["claude-3-haiku"],
                self.model_registry["openai"]["gpt-3.5-turbo"]
            ]
        }
        return recommendations.get(use_case, [])
    
    def list_available_models(self) -> Dict[str, List[str]]:
        """List all available models by provider."""
        available = {}
        for provider, models in self.model_registry.items():
            available[provider] = [
                model_info.model_name for model_info in models.values()
                if model_info.status == ModelStatus.AVAILABLE
            ]
        return available

# Global instance
model_validator = ProductionModelValidator()
