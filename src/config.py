from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    SECRET_KEY: str = Field(default="secret-key", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=1, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    COOKIE_NAME: str = Field(default="access_token", env="COOKIE_NAME")

    class Config:
        env_file = None


settings = Settings()
