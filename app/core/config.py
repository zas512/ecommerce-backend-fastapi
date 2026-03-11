from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, field_validator
from typing import List, Union


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENV_MODE: str = "dev"
    ALLOWED_HOSTS: Union[List[str], str] = ["localhost", "127.0.0.1"]
    BACKEND_CORS_ORIGINS: Union[List[str], str] = ["localhost"]

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field
    @property
    def log_level(self) -> str:
        return "warning" if self.ENV_MODE == "prod" else "debug"

    @computed_field
    @property
    def is_dev(self) -> bool:
        return self.ENV_MODE == "dev"

    @field_validator("ALLOWED_HOSTS", "BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_list(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i]
        return v

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", case_sensitive=True
    )


settings = Settings()  # type: ignore[call-arg]
