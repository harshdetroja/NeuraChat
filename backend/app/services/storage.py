import boto3
from botocore.client import Config
from app.core.config import settings

class Storage:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL,
            config=Config(signature_version='s3v4')
        )

    def ensure_bucket_exists(self):
        try:
            self.s3.head_bucket(Bucket=settings.S3_BUCKET_NAME)
        except self.s3.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                self.s3.create_bucket(Bucket=settings.S3_BUCKET)
            else:
                raise
    
    def upload_file_to_s3(self, file_bytes: bytes, object_key: str, content_type: str = "application/octet-stream") -> str:
        self.ensure_bucket_exists()
        self.s3.put_object(
            Bucket=settings.S3_BUCKET,
            Key=object_key,
            Body=file_bytes,
            ContentType=content_type
        )
        return object_key
    
    def delete_file_from_s3(self, file_name):
        self.s3.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=file_name)
    
storage_service = Storage()