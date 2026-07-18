from pydantic_settings import BaseSettings, SettingsConfigDict


class __Settings(BaseSettings):
    DATABASE_URL: str
    LOG_LEVEL: str
    ENVIRONMENT: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = __Settings()
