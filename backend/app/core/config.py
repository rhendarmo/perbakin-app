from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Perbakin API"
    ENV: str = "dev"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
