from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Read from the environment, or from backend/.env for local dev (see .env.example).
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str  # required: SQLite locally, PostgreSQL in docker/k8s
    cors_origins: str = "http://localhost:5173,http://localhost:8080"
    low_stock_threshold: int = 10


settings = Settings()
