import logging
import os
from functools import lru_cache

from pydantic_settings import BaseSettings

log = logging.getLogger("uvicorn")


_db_host = os.getenv("DB_HOST", "localhost")
_db_port = os.getenv("DB_PORT", "5433")
_db_user = os.getenv("DB_USER", "postgres")
_db_name = os.getenv("DB_NAME", "core")
_db_password = os.getenv("DB_PASSWORD", "postgres")


class Settings(BaseSettings):
    aws_region: str = os.getenv("AWS_DEFAULT_REGION", "")
    database_url: str = (
        f"postgres://{_db_user}:{_db_password}@{_db_host}:{_db_port}/{_db_name}"
    )
    environment: str = os.getenv("ENV", "dev")
    host: str = os.getenv("HOST_URL", "localhost")
    limit: int = os.getenv("LIMIT", 200)
    testing: bool = 0


@lru_cache()
def get_settings() -> Settings:
    log.info("Loading configuration from environment")
    return Settings()
