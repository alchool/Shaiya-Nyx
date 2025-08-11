# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    SECRET_KEY: str
    DB_URL: str  # es: mssql+pyodbc://user:password@windows-server-ip/dbname?driver=ODBC+Driver+17+for+SQL+Server
    JWT_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    STRIPE_SECRET: str
    PAYPAL_WEBHOOK_ID: str
    PAYPAL_CLIENT_ID: str
    PAYPAL_CLIENT_SECRET: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
