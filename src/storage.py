import json
import boto3
from botocore.exceptions import ClientError
from .utils import logger

s3 = boto3.client('s3')

def read_state(bucket, key):
    """S3에서 상태 정보를 읽어옵니다."""
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return [] if 'seen_ids' in key else {}
        logger.error(f"S3 read error: {e}")
        raise

def write_state(bucket, key, data):
    """S3에 상태 정보를 저장합니다."""
    try:
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data, ensure_ascii=False),
            ContentType='application/json'
        )
    except ClientError as e:
        logger.error(f"S3 write error: {e}")
        raise
