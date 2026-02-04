import os
import json
import logging
from dotenv import load_dotenv

# .env 파일이 있으면 로드
load_dotenv()

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_config():
    """
    환경 변수 또는 기본 설정값을 반환합니다.
    실제 운영 시에는 AWS SSM Parameter Store 등을 연동할 수 있습니다.
    """
    return {
        "min_budget": int(os.environ.get("MIN_BUDGET", 50000000)),
        "include_categories": os.environ.get("INCLUDE_CATEGORIES", "IT,SW").split(","),
        "exclude_keywords": os.environ.get("EXCLUDE_KEYWORDS", "재공고,취소").split(","),
        "s3_bucket": os.environ.get("S3_BUCKET", "market-notify-state"),
        "api_key": os.environ.get("decoding", ""),
        "api_endpoint": os.environ.get("API_ENDPOINT", "")
    }
