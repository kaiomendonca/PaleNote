from pydantic_settings import BaseSettings, SettingsConfigDict


class __Settings(BaseSettings):
    DATABASE_URL: str
    LOG_LEVEL: str
    ENVIRONMENT: str
    SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = __Settings()
