from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

LOG_DEFAULT_FORMAT = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
BASE_DIR = Path.cwd()


class Paths:
    temp: Path = BASE_DIR / 'temp'
    sessions: Path = BASE_DIR / 'sessions'
    logs: Path = BASE_DIR / 'logs'


class Telegram(BaseModel):
    token: str = Field(..., description="Token telegram bot")
    admins_id: list[int] = Field(..., description="Admins ID")
    webhook_id_base_bot: str = Field(..., )


class Game(BaseModel):
    url_template: str = Field(
        ...,
        description="Шаблон URL игры с {game_id}. Пример: 'https://example.com/game/{game_id}/'",
        examples=["https://example.com/game/{game_id}/"]
    )

    bot_ref_template: str = Field(
        ...,
        description="Опциональный шаблон реф-ссылки с {ref_id}. Пример: 'https://t.me/example_bot?start=ref_{ref_id}'",
        examples=["https://t.me/example_bot?start=ref_{ref_id}"]
    )


class GunicornConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8080
    workers: int = 1
    timeout: int = 900


class LoggingConfig(BaseModel):
    log_level: Literal[
        'debug',
        'info',
        'warning',
        'error',
        'critical',
    ] = 'info'
    log_format: str = LOG_DEFAULT_FORMAT


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10
    is_now_updated_db: bool = False

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env",),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )

    APP_NAME: str = Field(env="APP_NAME", default="FastAPI Application")
    DEBUG: bool = Field(env="DEBUG", default=False)
    paths: Paths = Paths()
    gunicorn: GunicornConfig = GunicornConfig()
    db: DatabaseConfig
    logging: LoggingConfig = LoggingConfig()
    tg: Telegram

    WEBHOOK_SECRET: str
    WEBHOOK_BASE_URL: str = "http://127.0.0.1:8000"
    ENV: str


# Экземпляр настроек
settings = Settings()
