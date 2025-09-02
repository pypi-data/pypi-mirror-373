from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global settings for the Buckeye SDK.

    This class manages configuration values loaded from environment variables
    and provides global access to settings throughout the application.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    buckeye_telemetry_url: str = Field(
        default="http://localhost:8765/api",  # https://telemetry.hud.so/v3/api
        description="Base URL for the Buckeye API",
        validation_alias="BUCKEYE_TELEMETRY_URL",
    )

    buckeye_mcp_url: str = Field(
        default="http://localhost:8765/mcp",  # https://mcp.hud.so/v3/mcp
        description="Base URL for the MCP Server",
        validation_alias="BUCKEYE_MCP_URL",
    )

    api_key: str | None = Field(
        default=None,
        description="API key for authentication with the Buckeye API",
        validation_alias="BUCKEYE_API_KEY",
    )

    anthropic_api_key: str | None = Field(
        default=None,
        description="API key for Anthropic models",
        validation_alias="ANTHROPIC_API_KEY",
    )

    openai_api_key: str | None = Field(
        default=None,
        description="API key for OpenAI models",
        validation_alias="OPENAI_API_KEY",
    )

    wandb_api_key: str | None = Field(
        default=None,
        description="API key for Weights & Biases",
        validation_alias="WANDB_API_KEY",
    )

    prime_api_key: str | None = Field(
        default=None,
        description="API key for Prime Intellect",
        validation_alias="PRIME_API_KEY",
    )

    telemetry_enabled: bool = Field(
        default=True,
        description="Enable telemetry for the Buckeye SDK",
        validation_alias="BUCKEYE_TELEMETRY_ENABLED",
    )

    buckeye_logging: bool = Field(
        default=True,
        description="Enable fancy logging for the Buckeye SDK",
        validation_alias="BUCKEYE_LOGGING",
    )

    log_stream: str = Field(
        default="stdout",
        description="Stream to use for logging output: 'stdout' or 'stderr'",
        validation_alias="BUCKEYE_LOG_STREAM",
    )


# Create a singleton instance
settings = Settings()


# Add utility functions for backwards compatibility
def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
