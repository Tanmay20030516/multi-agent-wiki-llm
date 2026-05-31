"""
core/config.py

Single source of truth for all application settings.
Reads from environment variables (loaded from .env by Docker or python-dotenv).

Usage anywhere in the codebase:
    from core.config import settings
    print(settings.gemini_api_key) # any other attribute
"""

from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator

# Explicitly load .env into os.environ before Settings() runs.
# pydantic-settings also reads env_file, but doing this upfront ensures
# the values are available regardless of how the process is launched
# (e.g. system uvicorn vs venv uvicorn).
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
if _ENV_FILE.exists():
    try:
        from dotenv import load_dotenv as _load_dotenv
        _load_dotenv(_ENV_FILE, override=False)
    except ImportError:
        pass


class Settings(BaseSettings):
    """
    All settings are read from environment variables.
    Pydantic-settings handles type coercion and validation automatically.
    Missing required fields raise a clear error at startup — fail fast.
    """

    # model_config = SettingsConfigDict(
    #     env_file=".env",  # loaded when running locally (not in Docker)
    #     env_file_encoding="utf-8",
    #     case_sensitive=False,  # GEMINI_API_KEY == gemini_api_key
    #     extra="ignore",  # silently ignore unknown env vars
    # )
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM API Keys
    gemini_api_key: str = Field(..., description="Google AI Studio API key")
    groq_api_key: str = Field(..., description="Groq API key")

    # Model Names
    maintenance_model: str = Field(
        default="gemini-2.5-flash",
        description="Model used by the maintenance agent (ingest, lint, promote)",
    )
    query_model: str = Field(
        default="meta-llama/llama-4-scout-17b-16e-instruct",
        description="Model used by the query agent (fast chat responses)",
    )
    query_model_fallback: str = Field(
        default="llama-3.1-8b-instant",
        description="Fallback query model if primary rate-limits or fails",
    )

    # Data Paths
    data_path: Path = Field(
        default=Path("/data"),
        description="Root of the data volume. Contains raw/ and wiki/ subdirs.",
    )

    # Agent Behaviour
    max_agent_iterations: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Hard cap on tool-calling iterations per agent run.",
    )
    max_tokens: int = Field(
        default=8192,
        ge=256,
        description="Max tokens the LLM can generate in a single call.",
    )
    maintenance_temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Temperature for maintenance agent. Low = consistent output.",
    )
    query_temperature: float = Field(
        default=0.4,
        ge=0.0,
        le=2.0,
        description="Temperature for query agent. Slightly higher = natural tone.",
    )

    # Server
    backend_host: str = Field(default="0.0.0.0")
    backend_port: int = Field(default=8000, ge=1, le=65535)

    # Logging
    log_level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Standard Python logging level.",
    )

    # Derived paths (computed, not read from env)
    # These are properties so they always stay in sync with data_path.
    # Access them the same way: settings.wiki_path, settings.raw_path, etc.

    @property
    def wiki_path(self) -> Path:
        """Root of the LLM-maintained wiki directory."""
        return self.data_path / "wiki"

    @property
    def raw_path(self) -> Path:
        """Root of the immutable raw sources directory."""
        return self.data_path / "raw"

    @property
    def schema_path(self) -> Path:
        return self.wiki_path / "schema.md"

    @property
    def index_path(self) -> Path:
        return self.wiki_path / "index.md"

    @property
    def log_path(self) -> Path:
        return self.wiki_path / "log.md"

    # Startup validation
    @model_validator(mode="after")
    def validate_data_path_exists(self) -> "Settings":
        """
        Warn if data_path doesn't exist yet.
        We don't hard-fail here because the volume may not be mounted
        until Docker Compose starts. The wiki_manager will handle this.
        """
        if not self.data_path.exists():
            import warnings

            warnings.warn(
                f"DATA_PATH '{self.data_path}' does not exist. "
                "Run scripts/init_wiki.py before starting the server.",
                stacklevel=2,
            )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.

    Using lru_cache means the .env file is read exactly once at startup,
    not on every import. Call get_settings() everywhere; don't instantiate
    Settings() directly.

    In tests, clear the cache with get_settings.cache_clear() and set
    environment variables before calling get_settings() again.
    """
    return Settings()


# Convenience alias — most modules just do:
#   from core.config import settings
settings = get_settings()
