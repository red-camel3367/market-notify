import os
import json
from datetime import datetime, timedelta, timezone
from src.utils import logger, get_config
from src.api import fetch_api
from src.processor import normalize_data
from src.notifier import send_slack_notification

def handle(event, context):
    """
    AWS Lambda Entry Point
    """
    try:
        logger.info("--- Starting Market Notify Lambda ---")
        
        # 1. 설정 로드
        config = get_config()
        if not config.get('api_key'):
            logger.error("API_KEY (decoding) environment variable is not set.")
            return {"statusCode": 500, "body": "Configuration error"}
        
        # 2. API 호출 준비
        api_url = config['api_endpoint'] + "getBidPblancListInfoServcPPSSrch"
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
        
        logger.info(f"Target Date (KST Yesterday): {yesterday_str}")
        
        # 3. 조합 반복 처리 (Keywords x Regions)
        for nm in nm_list:
            if not nm: continue
            for rgn in rgn_list:
                if not rgn: continue
                
                params = {
                    "numOfRows": 30, # 조금 넉넉하게 조회
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

        logger.info(f"Total unique items aggregated: {len(aggregate_items)}")

        # 4. 데이터 처리 (정규화)
        normalized = normalize_data(aggregate_items)

        # 5. 알림 발송
        if normalized:
            slack_webhook = os.environ.get("SLACK_WEBHOOK_URL")
            if slack_webhook:
                logger.info("Sending Slack notification...")
                send_slack_notification(slack_webhook, normalized)
            else:
                logger.warning("SLACK_WEBHOOK_URL not set. Logging items instead.")
                for item in normalized:
                    logger.info(f"New Item: {item.get('title')} ({item.get('budget')}원)")
        else:
            logger.info("No items found to notify.")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Success. Notified {len(normalized)} items."}, ensure_ascii=False)
        }

    except Exception as e:
        logger.error(f"Execution failed: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

if __name__ == "__main__":
    # 로컬 테스트용 실행
    handle(None, None)