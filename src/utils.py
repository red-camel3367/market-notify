import os
import logging


# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_config():
    """
    환경 변수 또는 기본 설정값을 반환합니다.
    """
    return {
        "api_key": os.environ.get("decoding", ""),
        "api_endpoint": os.environ.get("API_ENDPOINT", ""),
        "include_keywords": os.environ.get("INCLUDE_KEYWORDS", "").split(","),
        "region_codes": os.environ.get("REGION_CODES", "").split(",")
    }