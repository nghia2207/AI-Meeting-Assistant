"""
S3 Service - Upload audio files to AWS S3
"""
import boto3
from botocore.exceptions import ClientError
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

class S3Service:
    """Service để upload file lên S3"""

    def __init__(self):
        aws_key = os.getenv('AWS_ACCESS_KEY_ID', '')
        aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY', '')

        # Fail fast if credentials are placeholders
        if not aws_key or aws_key.startswith('your-') or not aws_secret or aws_secret.startswith('your-'):
            raise ValueError('AWS S3 credentials not configured (using placeholders)')

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('AWS_S3_BUCKET', 'ai-meeting-audio')

    def upload_audio(self, file_data, file_name=None, content_type='audio/webm'):
        """Upload audio file to S3"""
        try:
            if file_name is None:
                file_name = f"recordings/{uuid.uuid4()}.webm"

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=file_data,
                ContentType=content_type
            )

            # Generate URL
            region = os.getenv('AWS_REGION', 'us-east-1')
            url = f"https://{self.bucket_name}.s3.{region}.amazonaws.com/{file_name}"
            return url

        except ClientError as e:
            print(f'S3 upload error: {e}')
            raise e

    def get_audio_url(self, key):
        """Lấy URL của file trong S3"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=3600  # 1 hour
            )
            return url
        except ClientError as e:
            print(f'S3 URL generation error: {e}')
            raise e

    def delete_audio(self, key):
        """Xóa file khỏi S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            print(f'S3 delete error: {e}')
            raise e

# Singleton instance
_s3_service = None

def get_s3_service():
    global _s3_service
    if _s3_service is None:
        _s3_service = S3Service()
    return _s3_service