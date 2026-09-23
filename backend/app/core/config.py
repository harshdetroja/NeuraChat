import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "NeuraChat"
    VERSION: str = "0.1.0"
    
    # Security
    ACCESS_SECRET_KEY: str = os.getenv("ACCESS_SECRET_KEY", "default-access-secret-key-change-in-production")
    REFRESH_SECRET_KEY: str = os.getenv("REFRESH_SECRET_KEY", "default-refresh-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///neurachat.db")
    MAX_TOTAL_SIZE: int = 50 * 1024 * 1024

settings = Settings()

