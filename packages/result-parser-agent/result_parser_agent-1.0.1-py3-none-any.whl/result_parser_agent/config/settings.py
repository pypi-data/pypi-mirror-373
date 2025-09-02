"""Configuration management for the results parser agent."""

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings, Field, SecretStr, validator

# Explicitly load .env from current working directory
load_dotenv()


class APIConfig(BaseSettings):
    """API configuration class for the results parser agent."""

    PARSER_REGISTRY_URL: str = Field(default="http://10.138.172.118:8001")
    PARSER_REGISTRY_TIMEOUT: int = Field(default=30)


class ParserConfig(BaseSettings):
    """Unified configuration class for the results parser agent."""

    # LLM Configuration
    LLM_PROVIDER: str = Field(
        default="openai",
        description="LLM provider (groq, openai, anthropic, ollama, google)",
    )
    LLM_MODEL: str = Field(default="gpt-4o", description="LLM model to use")

    # Script Downloader Configuration
    SCRIPTS_BASE_URL: str = Field(
        default="git@github.com:AMD-DEAE-CEME/epdw2.0_parser_scripts.git",
        description="SSH git URL for the scripts repository",
    )
    SCRIPTS_CACHE_DIR: str = Field(
        default="~/.cache/result-parser/scripts",
        description="Local directory to cache downloaded scripts",
    )
    SCRIPTS_CACHE_TTL: int = Field(
        default=3600, description="Script cache TTL in seconds (1 hour)"
    )

    # API Keys (following your existing pattern)
    # GROQ_API_KEY: SecretStr = Field(..., description="Groq API key")
    OPENAI_API_KEY: SecretStr = Field(..., description="OpenAI API key")
    # GOOGLE_API_KEY: SecretStr = Field(..., description="Google API key")

    # Agent Configuration
    # AGENT_DEBUG: bool = Field(default=False, description="Enable debug mode")

    # Environment variable settings
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @validator("OPENAI_API_KEY")
    def validate_openai_api_key(cls, v: SecretStr):
        """Validate OpenAI API key format (following your existing pattern)."""
        secret = v.get_secret_value()
        if not secret.startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format")
        return v


settings = ParserConfig()
