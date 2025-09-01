"""Configuration management for the Video File Organizer application."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from nichi.constants import CONFIG_PATH_TEMPLATE
from nichi.exceptions import ConfigurationError


class ConfigManager:
    """Manages application configuration from environment variables."""

    def __init__(self) -> None:
        """Initialize the configuration manager."""
        self._load_environment()

    def _load_environment(self) -> bool:
        """
        Load environment variables from the standardized config path.

        Configuration loading order:
        1. ~/.config/nichi/.env (standardized location)
        2. System environment variables only

        Returns:
            True if .env file was found and loaded, False otherwise
        """
        # Try standardized config directory only
        expanded_path = os.path.expanduser(CONFIG_PATH_TEMPLATE)
        config_path = Path(expanded_path)
        path_exists = config_path.exists()
        if path_exists:
            load_dotenv(config_path)
            return True

        # Fall back to system environment variables only
        return False

    def get_api_key(self) -> str:
        """Get Google AI API key from environment."""
        from nichi.constants import ENV_GOOGLE_AI_API_KEY

        api_key = os.getenv(ENV_GOOGLE_AI_API_KEY)
        if not api_key:
            error_message = (
                f"{ENV_GOOGLE_AI_API_KEY} not found. Please set it in:\n"
                f"1. {CONFIG_PATH_TEMPLATE}\n"
                "2. System environment variables\n"
            )
            raise ConfigurationError(
                error_message,
                ENV_GOOGLE_AI_API_KEY,
            )
        return api_key

    def get_config_value(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value with fallback."""
        config_value = os.getenv(key, default)
        return config_value

    def get_int_config_value(self, key: str, default: Optional[int] = None) -> int:
        """Get integer configuration value with fallback."""
        default_string = str(default) if default is not None else None
        value = self.get_config_value(key, default_string)
        if value is None:
            return default if default is not None else 0
        try:
            int_value = int(value)
            return int_value
        except ValueError as e:
            error_message = "Invalid integer value for %s: %s" % (key, value)
            raise ConfigurationError(error_message, key) from e

    def get_float_config_value(self, key: str, default: Optional[float] = None) -> float:
        """Get float configuration value with fallback."""
        default_string = str(default) if default is not None else None
        value = self.get_config_value(key, default_string)
        if value is None:
            return default if default is not None else 0.0
        try:
            float_value = float(value)
            return float_value
        except ValueError as e:
            error_message = "Invalid float value for %s: %s" % (key, value)
            raise ConfigurationError(error_message, key) from e


# Global configuration instance
config = ConfigManager()
