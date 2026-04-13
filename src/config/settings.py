from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False

    llm_model: str = "gemini/gemini-2.5-flash"
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 3

    log_level: str = "INFO"
    environment: str = "production"
