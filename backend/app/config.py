import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/smarteval")
    SQLITE_URL: str = os.getenv("SQLITE_URL", "sqlite:///./smarteval.db")
    USE_SQLITE: bool = os.getenv("USE_SQLITE", "True").lower() in ("true", "1", "yes")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "949f28c5a2c4e20798e4d372fa05b8cf0f230da37194f4a3de07b6bf89ab1e6d")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    USE_MOCK_AI: bool = os.getenv("USE_MOCK_AI", "True").lower() in ("true", "1", "yes")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
