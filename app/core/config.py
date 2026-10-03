from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    SECRET: str = "secret-key-change-me"

    # Configuración SMTP para Gmail
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_NAME: str = "SaaS Citas"
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_TLS: bool = True

    # URL del Frontend (para redirigir los enlaces de verificación y recuperación)
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
