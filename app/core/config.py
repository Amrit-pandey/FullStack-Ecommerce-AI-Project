# Pydantic Settings (ENV variables, SECRET_KEY, DB_URL)
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    # _JWT
    secret_key: SecretStr
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    # _Database
    database_url: str

    # _Redis
    redis_host: str
    redis_port: int

    # _Resend
    resend_api_key: SecretStr



settings = Settings()