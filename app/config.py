from pydantic import BaseSettings


class Settings(BaseSettings):
    ENV_VAR: str


settings = Settings()