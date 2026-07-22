from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "BackendDeveloperLanding"
    app_owner_name: str = "Developer"
    app_owner_email: str = "owner@example.com"
    secret_key: str = "change-me"
    debug: bool = False

    ai_api_key: str = ""
    ai_api_base_url: str = "https://apihub.agnes-ai.com/v1"
    ai_model: str = "agnes-2.0-flash"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_from: str = ""

    rate_limit_requests: int = 10
    rate_limit_window_seconds: int = 60

    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = base_dir / "data"
    logs_dir: Path = base_dir / "logs"


settings = Settings()
