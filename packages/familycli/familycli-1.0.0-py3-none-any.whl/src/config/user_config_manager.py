"""
Production-ready user configuration manager.
Manages user-specific config in ~/.familyai/
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class UserConfigManager:
    """Manages user-specific configuration in user's home directory."""
    
    def __init__(self):
        self.config_dir = self._get_user_config_dir()
        self._ensure_config_dir_exists()
        
    def _get_user_config_dir(self) -> Path:
        """Get user-specific config directory."""
        home = Path.home()
        return home / ".familyai" / "config"
    
    def _ensure_config_dir_exists(self):
        """Ensure config directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def get_default_personas_path(self) -> Path:
        """Get path to user's default personas file."""
        return self.config_dir / "default_personas.json"
    
    def get_user_settings_path(self) -> Path:
        """Get path to user's settings file."""
        return self.config_dir / "user_settings.json"
    
    def initialize_default_config(self):
        """Initialize default configuration files if they don't exist."""
        # Initialize default personas
        personas_path = self.get_default_personas_path()
        if not personas_path.exists():
            self._create_default_personas_file(personas_path)
            
        # Initialize user settings
        settings_path = self.get_user_settings_path()
        if not settings_path.exists():
            self._create_default_settings_file(settings_path)
    
    def _create_default_personas_file(self, path: Path):
        """Create default personas configuration file by copying from main config."""
        try:
            # Copy from the main config/default_personas.json file
            import shutil
            main_personas_path = Path(__file__).parent.parent.parent / "config" / "default_personas.json"

            if main_personas_path.exists():
                shutil.copy2(main_personas_path, path)
                logger.info(f"Copied enhanced personas from {main_personas_path} to {path}")
                return
            else:
                logger.warning(f"Main personas file not found at {main_personas_path}, creating basic personas")
        except Exception as e:
            logger.error(f"Failed to copy main personas file: {e}, creating basic personas")

        # Fallback: create basic personas if copy fails
        default_personas = {
            "personas": [
                {
                    "name": "Grandma Rose",
                    "age": 72,
                    "description": "Warm, wise grandmother who loves sharing stories and giving advice",
                    "backstory": "Retired teacher, loves gardening and baking, family matriarch",
                    "personality_traits": ["loving", "patient", "wise", "empathetic", "traditional"],
                    "tone": "warm and nurturing",
                    "language_prefs": "en-US",
                    "llm_provider": "groq",
                    "llm_model": "llama-3.1-8b-instant",
                    "response_instructions": "Respond as a loving grandmother with wisdom and warmth. Share gentle advice and family stories when appropriate.",
                    "active": True
                },
                {
                    "name": "Uncle Joe",
                    "age": 45,
                    "description": "Funny tech enthusiast who keeps everyone laughing",
                    "backstory": "IT professional, loves gadgets and making jokes, family comedian",
                    "personality_traits": ["funny", "tech_savvy", "optimistic", "supportive", "modern"],
                    "tone": "casual and humorous",
                    "language_prefs": "en-US",
                    "llm_provider": "groq",
                    "llm_model": "llama-3.1-8b-instant",
                    "response_instructions": "Respond with humor and tech knowledge. Make light jokes and reference technology when relevant.",
                    "active": True
                }
            ]
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default_personas, f, indent=2, ensure_ascii=False)
        logger.info(f"Created fallback personas file at {path}")
        
        logger.info(f"Created default personas file at {path}")
    
    def _create_default_settings_file(self, path: Path):
        """Create default user settings file."""
        default_settings = {
            "default_llm_provider": "groq",
            "default_llm_model": "llama-3.1-8b-instant",
            "conversation_settings": {
                "max_response_length": 200,
                "response_style": "natural",
                "enable_streaming": True
            },
            "family_dynamics": {
                "conversation_style": "natural_family_chat",
                "response_timing": "realistic",
                "personality_interactions": "dynamic"
            }
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created default settings file at {path}")
    
    def load_personas(self) -> Dict[str, Any]:
        """Load user's personas configuration."""
        personas_path = self.get_default_personas_path()
        
        if not personas_path.exists():
            self.initialize_default_config()
        
        try:
            with open(personas_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load personas config: {e}")
            # Return minimal fallback
            return {"personas": []}
    
    def save_personas(self, personas_config: Dict[str, Any]):
        """Save user's personas configuration."""
        personas_path = self.get_default_personas_path()
        
        try:
            with open(personas_path, 'w', encoding='utf-8') as f:
                json.dump(personas_config, f, indent=2, ensure_ascii=False)
            logger.info("Saved personas configuration")
        except Exception as e:
            logger.error(f"Failed to save personas config: {e}")
            raise
    
    def load_user_settings(self) -> Dict[str, Any]:
        """Load user's settings."""
        settings_path = self.get_user_settings_path()
        
        if not settings_path.exists():
            self.initialize_default_config()
        
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load user settings: {e}")
            # Return minimal fallback
            return {
                "default_llm_provider": "groq",
                "default_llm_model": "llama-3.1-8b-instant"
            }
    
    def save_user_settings(self, settings: Dict[str, Any]):
        """Save user's settings."""
        settings_path = self.get_user_settings_path()
        
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            logger.info("Saved user settings")
        except Exception as e:
            logger.error(f"Failed to save user settings: {e}")
            raise
    
    def get_config_directory(self) -> Path:
        """Get the config directory path."""
        return self.config_dir

# Global instance
user_config = UserConfigManager()
