import os
import json
from datetime import datetime, timedelta, timezone
from src.utils import logger, get_config
from src.api import fetch_api
from src.processor import normalize_data
from src.notifier import send_slack_notification

def run_test():
    try:
        print("--- Starting Local Test ---")
        
        # 1. 설정 로드
        config = get_config()
        
        # API_KEY가 없을 경우를 대비한 안내
        if not config.get('api_key'):
            print("[Warning] API_KEY environment variable is not set.")
        
        # 2. API 호출 준비
        api_url = config['api_endpoint'] + "getBidPblancListInfoServcPPSSrch"
        print(f"[*] Using API endpoint: {api_url}")
        
        nm_list = config.get('include_keywords', [])
        rgn_list = config.get('region_codes', [])
        
        # 한국 시간(KST) 기준 어제 날짜 계산
        
        kst = timezone(timedelta(hours=9))
        yesterday = datetime.now(kst) - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y%m%d')
        
        bgn_dt = yesterday_str + '0000'
        end_dt = yesterday_str + '2359'
        
        aggregate_items = []
        seen_bid_ntce_nos = set()
        
        print(f"[*] Date range (KST Yesterday): {bgn_dt} ~ {end_dt}")
        
        # 조합 반복 처리
        for nm in nm_list:
            for rgn in rgn_list:
                print(f"[*] Fetching: keyword='{nm}', region='{rgn}'")
                params = {
                    "numOfRows": 10,
                    "pageNo": 1,
                    "serviceKey": config['api_key'],
                    "type": "json",
                    "inqryDiv": 1,
                    "bidNtceNm": nm,
                    "prtcptLmtRgnCd": rgn,
                    "inqryBgnDt": bgn_dt,
                    "inqryEndDt": end_dt
                }
                
                raw_data = fetch_api(api_url, params)
                
                if not raw_data:
                    print(f"    [!] Failed to fetch data for keyword='{nm}', region='{rgn}'")
                    continue

                body = raw_data.get('response', {}).get('body', {})
                items = body.get('items', [])
                
                if isinstance(items, dict):
                    items = [items]
                elif not isinstance(items, list):
                    items = []

                for item in items:
                    bid_ntce_no = item.get('bidNtceNo')
                    if bid_ntce_no and bid_ntce_no not in seen_bid_ntce_nos:
                        aggregate_items.append(item)
                        seen_bid_ntce_nos.add(bid_ntce_no)

        print(f"[*] Total unique items aggregated: {len(aggregate_items)}")

        # API 통합 응답을 output.json에 저장
        with open('output.json', 'w', encoding='utf-8') as f:
            json.dump(aggregate_items, f, ensure_ascii=False, indent=2)
        print("[*] Aggregated API response saved to 'output.json'.")

        # 4. 데이터 처리 (정규화)
        normalized = normalize_data(aggregate_items)

        print(f"[*] Normalized items: {len(normalized)}")

        # 5. 알림 발송
        if normalized:
            slack_webhook = os.environ.get("SLACK_WEBHOOK_URL")
            if slack_webhook:
                print("[*] Sending Slack notification...")
                send_slack_notification(slack_webhook, normalized)
            else:
                print("[!] SLACK_WEBHOOK_URL not set. Printing new items to console:")
                for item in normalized:
                    print(f"    - {item.get('title')} ({item.get('budget', 0)}원)")
        else:
            print("[*] No items found to notify.")

        print("--- Test Completed Successfully ---")

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
