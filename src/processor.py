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

def filter_items(items, config):
    """
    설정된 조건에 따라 필터링합니다.
    """
    filtered = []
    for item in items:
        # 예산 필터
        if item['budget'] < config['min_budget']:
            continue
        
        # 제외 키워드 필터
        if any(kw in item['title'] for kw in config['exclude_keywords']):
            continue
            
        # 포함 카테고리 필터 (제목에 키워드가 있는지 확인하는 예시)
        if not any(cat in item['title'] for cat in config['include_categories']):
            continue
            
        filtered.append(item)
    return filtered

def deduplicate(items, seen_ids):
    """
    중복된 공고를 제거합니다.
    """
    new_items = []
    current_seen_ids = set(seen_ids)
    
    for item in items:
        # 공고ID + 게시일 등을 조합하여 고유 키 생성
        unique_key = f"{item['id']}_{item['date']}"
        if unique_key not in current_seen_ids:
            new_items.append(item)
            current_seen_ids.add(unique_key)
            
    return new_items, list(current_seen_ids)
