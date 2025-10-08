"""Configuration management using Pydantic Settings"""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Slack Configuration
    slack_bot_token: str = Field(..., description="Slack Bot User OAuth Token (xoxb-...)")
    slack_app_token: str = Field(..., description="Slack App-Level Token (xapp-...)")
    slack_channels: Optional[str] = Field(
        default=None, description="Comma-separated list of channel IDs to monitor"
    )

    # Ollama Configuration
    ollama_model: str = Field(default="gemma3:4b", description="Ollama model name")
    ollama_host: str = Field(default="http://localhost:11434", description="Ollama server URL")

    # Download Configuration
    download_dir: str = Field(
        default="~/Library/Mobile Documents/com~apple~CloudDocs/Youtube",
        description="Directory to save downloaded videos",
    )

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/app.log", description="Log file path")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("download_dir")
    @classmethod
    def expand_download_dir(cls, v: str) -> str:
        """Expand user path and ensure directory exists"""
        expanded_path = Path(v).expanduser().resolve()
        expanded_path.mkdir(parents=True, exist_ok=True)
        return str(expanded_path)

    @field_validator("log_file")
    @classmethod
    def ensure_log_dir(cls, v: str) -> str:
        """Ensure log directory exists"""
        log_path = Path(v)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return str(log_path)

    @property
    def monitored_channels(self) -> set[str]:
        """Parse comma-separated channel IDs into a set"""
        if not self.slack_channels:
            return set()
        return {ch.strip() for ch in self.slack_channels.split(",") if ch.strip()}


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance"""
    global settings
    if settings is None:
        settings = Settings()
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment (useful for testing)"""
    global settings
    settings = Settings()
    return settings

