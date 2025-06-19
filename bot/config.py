from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LOG_DEFAULT_FORMAT = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"

BASE_DIR = Path(__file__).resolve().parent.parent


class Paths:
    temp: Path = BASE_DIR / 'temp'
    sessions: Path = BASE_DIR / 'sessions'
    logs: Path = BASE_DIR / 'logs'


class Telegram(BaseModel):
    token: str = Field(..., description="Token telegram bot")
    admins_id: list[int] = Field(..., description="Admins ID")


class DatabaseConfig(BaseModel):
    url: str = "sqlite+aiosqlite:///db.db"
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    # Флаг указывающий обновляется ли на данный момент база данных
    is_now_updated_db: bool = False

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class LoggingConfig(BaseModel):
    log_level: Literal[
        'debug',
        'info',
        'warning',
        'error',
        'critical',
    ] = 'info'
    log_format: str = LOG_DEFAULT_FORMAT


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    logging: LoggingConfig = LoggingConfig()
    paths: Paths = Paths()
    tg: Telegram
    db: DatabaseConfig = DatabaseConfig()

settings = Settings()
