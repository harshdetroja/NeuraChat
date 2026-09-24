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

    # Storage
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "default-aws-access-key-change-in-production")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "default-aws-secret-access-change-in-production")
    S3_REGION: str = os.getenv("S3_REGION", "default-aws-region-change-in-production")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "default-aws-s3-bucket-change-in-production")
    S3_ENDPOINT_URL: str = os.getenv("S3_ENDPOINT_URL", "default-aws-s3-endpoint-url-change-in-production")

settings = Settings()

