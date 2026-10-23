from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore",
  )

  app_title: str = "VaiBem Platform - School Journey"
  app_version: str = "0.1.0"
  database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/vaibem"
  database_echo: bool = False

  # JWT / Auth settings
  jwt_secret_key: str = "dev-secret-key-change-in-production"
  jwt_algorithm: str = "HS256"
  jwt_access_token_expire_minutes: int = 60
  jwt_refresh_token_expire_days: int = 30


settings = Settings()
