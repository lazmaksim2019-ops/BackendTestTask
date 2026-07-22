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

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:5500,http://localhost:8000"

    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = base_dir / "data"
    logs_dir: Path = base_dir / "logs"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
