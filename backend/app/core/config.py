"""
Application configuration — reads from environment variables via pydantic-settings.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "Groww Lens"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"

    # Database & Supabase
    DATABASE_URL: str = "sqlite+aiosqlite:///./groww_lens.db"
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # External APIs
    GEMINI_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    FINNHUB_API_KEY: str = ""

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def allowed_origins(self) -> List[str]:
        """Parsed list of allowed CORS origins."""
        return [item.strip() for item in self.ALLOWED_ORIGINS.split(",") if item.strip()]

    # Impact scoring weights (must sum to 1.0)
    WEIGHT_PRICE: float = 0.30
    WEIGHT_VOLUME: float = 0.25
    WEIGHT_NEWS: float = 0.20
    WEIGHT_VOLATILITY: float = 0.15
    WEIGHT_WATCHLIST: float = 0.10

    # Thresholds
    HIGH_IMPACT_THRESHOLD: int = 60     # Events above this score are "high impact"
    PRICE_SURGE_THRESHOLD: float = 2.0  # % change to qualify as a surge
    VOLUME_SPIKE_MULTIPLIER: float = 1.5  # x average volume to qualify as spike


settings = Settings()
