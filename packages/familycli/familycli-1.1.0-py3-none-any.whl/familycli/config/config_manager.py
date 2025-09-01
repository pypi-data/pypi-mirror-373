import os
import json
from typing import Any, Dict

class UserDirectoryManager:
    """
    Centralized manager for all user data directories.
    Ensures all components use the same base directory structure.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            # Use environment variable or default to .familyai
            self.base_dir = os.path.expanduser(os.getenv('FAMILYCLI_USER_DIR', '~/.familyai'))
            self.config_dir = os.path.join(self.base_dir, 'config')
            self.logs_dir = os.path.join(self.base_dir, 'logs')
            self.data_dir = os.path.join(self.base_dir, 'data')
            self.backups_dir = os.path.join(self.base_dir, 'backups')
            self.persona_packs_dir = os.path.join(self.base_dir, 'persona_packs')
            
            # Create all directories
            for dir_path in [self.base_dir, self.config_dir, self.logs_dir, 
                           self.data_dir, self.backups_dir, self.persona_packs_dir]:
                os.makedirs(dir_path, exist_ok=True)
            
            self._initialized = True
    
    def get_base_dir(self) -> str:
        """Get the base user directory."""
        return self.base_dir
    
    def get_config_dir(self) -> str:
        """Get the configuration directory."""
        return self.config_dir
    
    def get_logs_dir(self) -> str:
        """Get the logs directory."""
        return self.logs_dir
    
    def get_data_dir(self) -> str:
        """Get the data directory."""
        return self.data_dir
    
    def get_backups_dir(self) -> str:
        """Get the backups directory."""
        return self.backups_dir
    
    def get_persona_packs_dir(self) -> str:
        """Get the persona packs directory."""
        return self.persona_packs_dir
    
    def get_database_path(self) -> str:
        """Get the database file path."""
        return os.path.join(self.data_dir, 'familycli.db')
    
    def get_session_file(self) -> str:
        """Get the session file path."""
        return os.path.join(self.data_dir, 'session.json')
    
    def get_api_keys_file(self) -> str:
        """Get the API keys file path."""
        return os.path.join(self.data_dir, 'api_keys.json')
    
    def get_encryption_key_file(self) -> str:
        """Get the encryption key file path."""
        return os.path.join(self.data_dir, 'encryption.key')

class ConfigManager:
    """
    Centralized configuration manager for loading, overriding, and reloading config files.
    Usage:
        config = ConfigManager().load('llm_providers')
        value = ConfigManager().get('llm_providers', 'default_provider')
        ConfigManager().reload('llm_providers')
    """
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            # Use centralized user directory manager
            self.user_dir_manager = UserDirectoryManager()
            self.config_dir = self.user_dir_manager.get_config_dir()
        else:
            self.config_dir = config_dir
        self._cache: Dict[str, Dict[str, Any]] = {}

        # Ensure essential config files exist
        self._ensure_essential_configs()

    def load(self, name: str) -> Dict[str, Any]:
        """
        Load a config file and apply environment variable overrides.
        Args:
            name (str): Config file name (without .json).
        Returns:
            dict: Config dictionary.
        """
        if name in self._cache:
            return self._cache[name]
        path = os.path.join(self.config_dir, f'{name}.json')
        if not os.path.exists(path):
            raise FileNotFoundError(f'Config file not found: {path}')
        with open(path, 'r') as f:
            config = json.load(f)
        # Override with environment variables
        for key in config:
            env_key = f'{name.upper()}_{key.upper()}'
            if env_key in os.environ:
                config[key] = os.environ[env_key]
        self._cache[name] = config
        return config

    def reload(self, name: str) -> Dict[str, Any]:
        """
        Reload a config file, clearing cache.
        Args:
            name (str): Config file name.
        Returns:
            dict: Config dictionary.
        """
        if name in self._cache:
            del self._cache[name]
        return self.load(name)

    def get(self, name: str, key: str, default=None):
        """
        Get a config value by key, with optional default.
        Args:
            name (str): Config file name.
            key (str): Config key.
            default: Default value if key not found.
        Returns:
            Value from config or default.
        """
        config = self.load(name)
        return config.get(key, default)

    def _ensure_essential_configs(self):
        """Ensure essential config files exist in .familyai directory."""
        essential_configs = {
            'llm_providers.json': self._get_default_llm_providers_config(),
            'db_manager.json': self._get_default_db_config(),
            'app_config.json': self._get_default_app_config()
        }

        for filename, default_config in essential_configs.items():
            config_path = os.path.join(self.config_dir, filename)
            if not os.path.exists(config_path):
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)

    def _get_default_llm_providers_config(self):
        """Get default LLM providers configuration."""
        return {
            "providers": {
                "groq": {
                    "name": "Groq",
                    "base_url": "https://api.groq.com/openai/v1",
                    "auth_header": "Authorization",
                    "auth_prefix": "Bearer",
                    "streaming_supported": True,
                    "models": {
                        "llama-3.1-8b-instant": {
                            "name": "Llama 3.1 8B Instant",
                            "max_tokens": 8192,
                            "context_window": 131072,
                            "cost_per_1k_tokens": 0.00005
                        }
                    }
                },
                "openai": {
                    "name": "OpenAI",
                    "base_url": "https://api.openai.com/v1",
                    "auth_header": "Authorization",
                    "auth_prefix": "Bearer",
                    "streaming_supported": True,
                    "models": {
                        "gpt-4o-mini": {
                            "name": "GPT-4 Omni Mini",
                            "max_tokens": 16384,
                            "context_window": 128000,
                            "cost_per_1k_tokens": 0.00015
                        }
                    }
                },
                "anthropic": {
                    "name": "Anthropic",
                    "base_url": "https://api.anthropic.com",
                    "auth_header": "x-api-key",
                    "auth_prefix": "",
                    "streaming_supported": True,
                    "models": {
                        "claude-3-5-haiku-20241022": {
                            "name": "Claude 3.5 Haiku",
                            "max_tokens": 8192,
                            "context_window": 200000,
                            "cost_per_1k_tokens": 0.00025
                        }
                    }
                },
                "cerebras": {
                    "name": "Cerebras",
                    "base_url": "https://api.cerebras.ai/v1",
                    "auth_header": "Authorization",
                    "auth_prefix": "Bearer",
                    "streaming_supported": True,
                    "models": {
                        "llama3.1-8b": {
                            "name": "Llama 3.1 8B",
                            "max_tokens": 8192,
                            "context_window": 128000,
                            "cost_per_1k_tokens": 0.00006
                        }
                    }
                },
                "google": {
                    "name": "Google",
                    "base_url": "https://generativelanguage.googleapis.com/v1beta",
                    "auth_header": "Authorization",
                    "auth_prefix": "Bearer",
                    "streaming_supported": True,
                    "models": {
                        "gemini-1.5-flash": {
                            "name": "Gemini 1.5 Flash",
                            "max_tokens": 8192,
                            "context_window": 1000000,
                            "cost_per_1k_tokens": 0.000075
                        }
                    }
                }
            },
            "default_provider": "groq",
            "fallback_providers": ["openai", "anthropic", "cerebras", "google"],
            "rate_limits": {
                "requests_per_minute": 60,
                "tokens_per_minute": 90000,
                "concurrent_requests": 5
            },
            "retry_config": {
                "max_retries": 3,
                "backoff_factor": 2,
                "initial_delay": 1
            }
        }

    def _get_default_db_config(self):
        """Get default database configuration."""
        user_dir_manager = UserDirectoryManager()
        return {
            "db_url": f"sqlite:///{user_dir_manager.get_database_path()}",
            "pool_size": 5,
            "max_overflow": 10
        }

    def _get_default_app_config(self):
        """Get default app configuration."""
        user_dir_manager = UserDirectoryManager()
        return {
            "app_name": "Family AI CLI",
            "version": "1.0.0",
            "database_path": user_dir_manager.get_database_path(),
            "log_level": "INFO",
            "session_timeout_minutes": 120,
            "encryption_key_path": user_dir_manager.get_encryption_key_file()
        }
