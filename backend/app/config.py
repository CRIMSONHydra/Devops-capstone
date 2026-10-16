from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/ecommerce"
    cors_origins: str = "http://localhost:5173,http://localhost:8080"
    low_stock_threshold: int = 10


settings = Settings()
