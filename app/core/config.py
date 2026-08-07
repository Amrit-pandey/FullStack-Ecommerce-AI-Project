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

    # _AWS
    aws_access_key_id: SecretStr | None = None
    aws_secret_access_key: SecretStr | None = None
    aws_region: str
    aws_s3_bucket_name: str

    # _RabbitMQ
    rabbit_mq_url: str



settings = Settings()