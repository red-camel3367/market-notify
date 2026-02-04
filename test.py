import os
import json
from src.utils import logger, get_config
from src.api import fetch_api
from src.processor import normalize_data, filter_items, deduplicate
from src.notifier import send_slack_notification

# 로컬 테스트용 상태 읽기 함수
def read_state_local(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# 로컬 테스트용 상태 저장 함수
def write_state_local(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def run_test():
    try:
        print("--- Starting Local Test ---")
        
        # 1. 설정 로드
        config = get_config()
        
        # API_KEY가 없을 경우를 대비한 안내
        if not config.get('api_key'):
            print("[Warning] API_KEY environment variable is not set.")
            # 실제 테스트를 위해 임시로 입력받거나 설정을 권장
        
        state_file = 'state_seen_ids.json'
        
        # 2. 상태 로드 (Local File 기반)
        seen_ids = read_state_local(state_file)
        print(f"[*] Loaded {len(seen_ids)} seen IDs from '{state_file}'.")
        
        # 3. API 호출
        api_url = config['api_endpoint']
        print(f"[*] Using API endpoint: {api_url}")
        params = {
            "numOfRows": 10,
            "pageNo": 1,
            "serviceKey": config['api_key'],
            "type": "json",
            "inqryDiv": 1,
            "inqryBgnDt": '202602010000', # 날짜 범위가 없으면 데이터가 안 올 수 있음
            "inqryEndDt": '202602042300'
        }
        
        print(f"[*] Calling API: {api_url}")
        raw_data = fetch_api(api_url, params)
        
        if not raw_data:
            print("[!] API call failed or returned no data.")
            return

        # API 원본 응답을 output.json에 저장
        with open('output.json', 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        print("[*] Raw API response saved to 'output.json'.")

        # 4. 데이터 처리 (정규화 -> 필터링 -> 중복제거)
        # API 응답 구조에 따라 get() 체이닝은 수정이 필요할 수 있습니다.
        body = raw_data.get('response', {}).get('body', {})
        raw_items = body.get('items', [])
        
        if not isinstance(raw_items, list):
            # 일부 공공 API는 아이템이 하나일 때 dict로 줄 때가 있음
            if isinstance(raw_items, dict) and raw_items:
                raw_items = [raw_items]
            else:
                raw_items = []

        print(f"[*] Fetched {len(raw_items)} raw items from API.")
        
        normalized = normalize_data(raw_items)
        filtered = filter_items(normalized, config)
        new_items, updated_seen_ids = deduplicate(filtered, seen_ids)

        print(f"[*] Filtered items: {len(filtered)}")
        print(f"[*] New items after deduplication: {len(new_items)}")

        # 5. 알림 발송
        if new_items:
            slack_webhook = os.environ.get("SLACK_WEBHOOK_URL")
            if slack_webhook:
                print("[*] Sending Slack notification...")
                send_slack_notification(slack_webhook, new_items)
            else:
                print("[!] SLACK_WEBHOOK_URL not set. Printing new items to console:")
                for item in new_items:
                    print(f"    - {item.get('title')} ({item.get('budget', 0)}원)")
            
            # 6. 상태 업데이트 (Local File)
            write_state_local(state_file, updated_seen_ids)
            print(f"[*] Updated state saved to '{state_file}'.")
        else:
            print("[*] No new items found to notify.")

        print("--- Test Completed Successfully ---")

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
