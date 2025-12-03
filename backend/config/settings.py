"""
Configuration settings for the application.
Centralized configuration management with environment variable support.
"""
import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class MistralConfig:
    """Mistral AI API configuration."""
    api_key: str
    api_base_url: str = "https://api.mistral.ai/v1"
    model: str = "mistral-large-latest"
    max_tokens: int = 4096
    temperature: float = 0.7
    stream: bool = True


@dataclass
class ServerConfig:
    """Server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list = None

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000"]


@dataclass
class AppConfig:
    """Main application configuration."""
    mistral: MistralConfig
    server: ServerConfig


def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    mistral_api_key = os.getenv("MISTRAL_API_KEY", "")

    if not mistral_api_key:
        raise ValueError("MISTRAL_API_KEY environment variable is required")

    mistral_config = MistralConfig(
        api_key=mistral_api_key,
        api_base_url=os.getenv("MISTRAL_API_BASE_URL", "https://api.mistral.ai/v1"),
        model=os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
        max_tokens=int(os.getenv("MISTRAL_MAX_TOKENS", "4096")),
        temperature=float(os.getenv("MISTRAL_TEMPERATURE", "0.7"))
    )

    server_config = ServerConfig(
        host=os.getenv("SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVER_PORT", "8000")),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    )

    return AppConfig(mistral=mistral_config, server=server_config)
