import os
import json
from pathlib import Path
from typing import Dict, Any


class Config:
    _instance = None
    _config_file = Path.home() / '.unisonai' / 'config.json'
    _config: Dict[str, Any] = {
        'api_keys': {
            'gemini': None,
            'openai': None,
            'anthropic': None,
            'cohere': None,
            'groq': None,
            'mixtral': None,
            'helpingai': None,
            'xai': None,
            'cerebras': None,
        }
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Load configuration from file if it exists."""
        if self._config_file.exists():
            try:
                with open(self._config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self._config['api_keys'].update(
                        loaded_config.get('api_keys', {}))
            except Exception as e:
                print(f"Error loading config: {e}")

    def _save_config(self):
        """Save configuration to file."""
        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._config_file, 'w') as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def set_api_key(self, model: str = None, provider: str = None, api_key: str = None):
        """Set API key for a specific provider.
        
        Args:
            model: Model/provider name (e.g., 'gemini', 'openai')
            provider: Alias for model parameter (for backward compatibility)
            api_key: The API key to set
            
        Examples:
            config.set_api_key(model="gemini", api_key=os.getenv("GEMINI_API_KEY"))
            config.set_api_key("gemini", api_key=os.getenv("GEMINI_API_KEY"))
        """
        # Support both model= and provider= parameters
        provider_name = model or provider
        
        if provider_name is None:
            raise ValueError("Either 'model' or 'provider' parameter must be specified")
        
        if api_key is None:
            raise ValueError("api_key parameter is required")
            
        if provider_name in self._config['api_keys']:
            self._config['api_keys'][provider_name] = api_key
            self._save_config()
        else:
            raise ValueError(f"Unknown provider: {provider_name}. Available: {', '.join(self._config['api_keys'].keys())}")

    def get_api_key(self, model: str = None, provider: str = None) -> str:
        """Get API key for a specific provider.
        
        Args:
            model: Model/provider name (e.g., 'gemini', 'openai')
            provider: Alias for model parameter (for backward compatibility)
            
        Returns:
            API key string or None if not set
            
        Examples:
            key = config.get_api_key(model="gemini")
            key = config.get_api_key("gemini")
        """
        provider_name = model or provider
        
        if provider_name is None:
            raise ValueError("Either 'model' or 'provider' parameter must be specified")
            
        return self._config['api_keys'].get(provider_name)

    def get_all_api_keys(self) -> Dict[str, str]:
        """Get all API keys."""
        return self._config['api_keys'].copy()


# Create a global config instance
config = Config()
