from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://waste_management_r6dq_user:pc3cDMMJivdyungesGDSAothImmbCjkU@dpg-d154aep5pdvs73esfsmg-a/waste_management_r6dq"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()