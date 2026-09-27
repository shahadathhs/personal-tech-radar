from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "personal-tech-radar"
    debug: bool = True
    api_prefix: str = "/api"

    database_url: str = "postgresql+asyncpg://radar:radar@localhost:5544/radar"
    redis_url: str = "redis://localhost:16379/0"

    cors_origins: str = "http://localhost:3200"

    # AI provider — OpenAI-compatible endpoint. See modules/ai/provider.py.
    ai_provider: str = "zai"  # zai | openai | ollama
    ai_base_url: str = "https://api.z.ai/api/paas/v4"
    ai_api_key: str = ""
    ai_model: str = "glm-5.3"
    ai_fast_model: str = "glm-5.3-flash"

    # Telegram delivery.
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Digest schedule (local time).
    digest_time: str = "19:00"
    timezone: str = "Asia/Dhaka"

    # Ranking weights — the transparent baseline from GOAL.md §61.
    weight_relevance: float = 0.30
    weight_importance: float = 0.25
    weight_freshness: float = 0.15
    weight_novelty: float = 0.10
    weight_actionability: float = 0.10
    weight_source_quality: float = 0.10

    # Digest composition.
    digest_top_stories: int = 3
    digest_max_items: int = 12
    digest_max_per_category: int = 3
    freshness_decay_hours: float = 24.0

    # Ingestion limits.
    max_items_per_source_run: int = 50


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
