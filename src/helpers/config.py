from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    app_version: str
    api_prefix: str
    
    ALLOWED_FILE_TYPES: list[str]
    FILE_MAX_SIZE_MB: int
    FILE_DEFAULT_CHUNK_SIZE: int
    # MONGO DB SETTINGS
    MONGO_URL: str
    MONGO_DB_NAME: str


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


def get_settings() -> Settings:
    return Settings()