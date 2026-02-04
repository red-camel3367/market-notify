import requests
from .utils import logger

def send_slack_notification(webhook_url, items):
    """
    슬랙으로 신규 공고 알림을 보냅니다.
    """
    if not items:
        return

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                # "text": f"<!channel> 🔔 *신규 공고 탐지 ({len(items)}건)*"
                "text": f"🔔 *신규 공고 탐지 ({len(items)}건)*"
            }
        },
        {"type": "divider"}
    ]

    for item in items[:5]:  # 최대 5건까지만 상세 출력
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*[{item['org']}]* {item['title']}\n예산: {item['budget']:,}원\n<{item['url']}|상세보기>"
            }
        })

    if len(items) > 5:
        blocks.append({
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"외 {len(items)-5}건의 공고가 더 있습니다."}
            ]
        })

    try:
        response = requests.post(webhook_url, json={"blocks": blocks})
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Slack notification failed: {e}")
