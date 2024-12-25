from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseSettingsWithConfig(BaseSettings):
    """Родительский класс с настройками .env и экстра-атрибутов.
    Нужен, чтобы унаследовать эти настройки для всех классов настроек дальше"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )


class Settings(BaseSettingsWithConfig):
    """Модель настроек"""
    # Креды гигачата
    gigachat_api_token: str

    # Креды Telegram
    tg_token: str
    skip_updates: bool = True


settings = Settings()
