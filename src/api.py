import requests
import time
from .utils import logger

def fetch_api(api_url, params, retries=2):
    """
    공공 API를 호출합니다. 실패 시 재시도 로직을 포함합니다.
    """
    for i in range(retries + 1):
        try:
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()  # 또는 XML 파싱 로직
        except Exception as e:
            logger.warning(f"API call failed (attempt {i+1}): {e}")
            if i < retries:
                time.sleep(2)
            else:
                logger.error("Max retries reached. API call failed.")
                return None
