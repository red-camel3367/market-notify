import os
from src.utils import logger, get_config
from src.api import fetch_api
from src.processor import normalize_data, filter_items, deduplicate
from src.storage import read_state, write_state
from src.notifier import send_slack_notification

def lambda_handler(event, context):
    try:
        # 1. 설정 로드
        config = get_config()
        bucket = config['s3_bucket']
        
        # 2. 상태 로드 (S3)
        seen_ids = read_state(bucket, 'state/seen_ids.json')
        
        # 3. API 호출
        # 실제 API URL 및 파라미터는 공공데이터포털 사양에 맞춰 수정
        api_url = config['api_endpoint']
        params = {
            "serviceKey": config['api_key'],
            "type": "json",
            "numOfRows": 100
        }
        raw_data = fetch_api(api_url, params)
        
        if not raw_data:
            return {"statusCode": 500, "body": "API call failed"}

        # 4. 데이터 처리 (정규화 -> 필터링 -> 중복제거)
        raw_items = raw_data.get('response', {}).get('body', {}).get('items', [])
        normalized = normalize_data(raw_items)
        filtered = filter_items(normalized, config)
        new_items, updated_seen_ids = deduplicate(filtered, seen_ids)

        # 5. 알림 발송
        if new_items:
            slack_webhook = os.environ.get("SLACK_WEBHOOK_URL")
            if slack_webhook:
                send_slack_notification(slack_webhook, new_items)
            
            # 6. 상태 업데이트 (S3)
            write_state(bucket, 'state/seen_ids.json', updated_seen_ids)
            logger.info(f"Successfully processed {len(new_items)} new items.")
        else:
            logger.info("No new items found.")

        return {
            "statusCode": 200,
            "body": f"Processed {len(new_items)} new items."
        }

    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        return {
            "statusCode": 500,
            "body": str(e)
        }
