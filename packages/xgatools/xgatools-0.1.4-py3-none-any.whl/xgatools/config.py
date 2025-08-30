import os
from dotenv import load_dotenv
from typing import Optional
import logging


class Config:
    """Configuration management class for XGA Tools."""

    def __init__(self, env_file: str = ".env"):
        """
        Initialize configuration by loading from .env file.

        Args:
            env_file: Path to the .env file (default: ".env")
        """
        # Load environment variables from .env file
        load_dotenv(env_file)

        # Tavily API configuration
        self.TAVILY_API_KEY = self._get_env_var("TAVILY_API_KEY")

        # Firecrawl API configuration
        self.FIRECRAWL_API_KEY = self._get_env_var("FIRECRAWL_API_KEY")
        self.FIRECRAWL_URL = self._get_env_var("FIRECRAWL_URL", "https://api.firecrawl.dev")

        # Daytona configuration
        self.DAYTONA_API_KEY = self._get_env_var("DAYTONA_API_KEY")
        self.DAYTONA_SERVER_URL = self._get_env_var("DAYTONA_SERVER_URL", "https://app.daytona.io/api")
        self.DAYTONA_TARGET = self._get_env_var("DAYTONA_TARGET", "us")
        self.DAYTONA_IMAGE_NAME = self._get_env_var("DAYTONA_IMAGE_NAME", "kortix/suna:0.1.3")

        # Logging configuration
        self.LOG_LEVEL = self._get_env_var("LOG_LEVEL", "INFO")

        # Validate required configuration
        self._validate_config()

    def _get_env_var(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with optional default value.

        Args:
            key: Environment variable key
            default: Default value if key is not found

        Returns:
            Environment variable value or default
        """
        value = os.getenv(key, default)
        if value is None:
            logging.warning(f"Environment variable {key} not found and no default provided")
        return value

    def _validate_config(self):
        """Validate that required configuration values are present."""
        required_vars = {
            "TAVILY_API_KEY": self.TAVILY_API_KEY,
            "FIRECRAWL_API_KEY": self.FIRECRAWL_API_KEY,
            "DAYTONA_API_KEY": self.DAYTONA_API_KEY,
        }

        missing_vars = [key for key, value in required_vars.items() if not value]

        if missing_vars:
            error_msg = f"Missing required configuration variables: {', '.join(missing_vars)}"
            logging.error(error_msg)
            raise ValueError(error_msg)

    def get_tavily_config(self) -> dict:
        """Get Tavily API configuration."""
        return {
            "api_key": self.TAVILY_API_KEY
        }

    def get_firecrawl_config(self) -> dict:
        """Get Firecrawl API configuration."""
        return {
            "api_key": self.FIRECRAWL_API_KEY,
            "url": self.FIRECRAWL_URL
        }

    def get_daytona_config(self) -> dict:
        """Get Daytona configuration."""
        return {
            "api_key": self.DAYTONA_API_KEY,
            "server_url": self.DAYTONA_SERVER_URL,
            "target": self.DAYTONA_TARGET,
            "image_name": self.DAYTONA_IMAGE_NAME
        }

    def is_valid(self) -> bool:
        """
        Check if all required configuration is valid.

        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            self._validate_config()
            return True
        except ValueError:
            return False


# Global configuration instance
config = Config()


# Alternative function for backward compatibility
def get_config(env_file: str = ".env") -> Config:
    """
    Get configuration instance.

    Args:
        env_file: Path to the .env file

    Returns:
        Configuration instance
    """
    return Config(env_file)