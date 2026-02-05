import hashlib
from .utils import logger

def normalize_data(raw_items):
    """
    원본 데이터를 공통 포맷으로 정규화합니다.
    """
    normalized = []
    for item in raw_items:
        # API 응답 구조에 맞게 매핑 필요
        normalized.append({
            "id": item.get("bidNtceNo"),
            "title": item.get("bidNtceNm"),
            "org": item.get("ntceInsttNm"),
            "budget": int(item.get("presmptPrce", 0)),
            "date": item.get("bidNtceDt"),
            "url": item.get("bidNtceDtlUrl")
        })
    return normalized
