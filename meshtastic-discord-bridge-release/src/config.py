"""Configuration management for Meshtastic Discord Bridge."""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Application configuration loaded from environment variables."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        # Discord settings
        self.discord_bot_token: str = self._get_required_env("DISCORD_BOT_TOKEN")
        self.discord_channel_id: int = int(self._get_required_env("DISCORD_CHANNEL_ID"))
        
        # Meshtastic settings
        self.meshtastic_device: str = os.getenv("MESHTASTIC_DEVICE", "/dev/ttyACM0")
        
        # Application settings
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
        self.reconnect_delay: int = int(os.getenv("RECONNECT_DELAY", "5"))
        
        # Validate configuration
        self._validate()
        
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error.
        
        Args:
            key: Environment variable name
            
        Returns:
            Environment variable value
            
        Raises:
            ValueError: If environment variable is not set
        """
        value = os.getenv(key)
        if not value:
            raise ValueError(
                f"Required environment variable {key} is not set. "
                f"Please set it in your .env file or environment."
            )
        return value
    
    def _validate(self):
        """Validate configuration values."""
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            logger.warning(
                f"Invalid log level '{self.log_level}'. Using 'INFO'. "
                f"Valid levels: {', '.join(valid_log_levels)}"
            )
            self.log_level = "INFO"
        
        # Validate reconnect delay
        if self.reconnect_delay < 1:
            logger.warning(
                f"Invalid reconnect delay {self.reconnect_delay}. Using 5 seconds."
            )
            self.reconnect_delay = 5
            
        # Check if device exists (warning only, as it might appear later)
        if not Path(self.meshtastic_device).exists():
            logger.warning(
                f"Meshtastic device {self.meshtastic_device} not found. "
                f"Make sure the device is connected."
            )
    
    def __repr__(self) -> str:
        """Return safe string representation (hiding sensitive data)."""
        return (
            f"Config("
            f"discord_channel_id={self.discord_channel_id}, "
            f"meshtastic_device='{self.meshtastic_device}', "
            f"log_level='{self.log_level}', "
            f"reconnect_delay={self.reconnect_delay}"
            f")"
        )


# Global config instance
config: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global configuration instance.
    
    Returns:
        Global Config instance
    """
    global config
    if config is None:
        config = Config()
    return config
