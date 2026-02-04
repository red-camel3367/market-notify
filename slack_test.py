import os
from dotenv import load_dotenv
from src.notifier import send_slack_notification

# .env 로드
load_dotenv()

def test_slack():
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    
    if not webhook_url:
        print("[!] SLACK_WEBHOOK_URL이 .env 파일에 설정되어 있지 않습니다.")
        return

    # 테스트용 가짜 데이터 (src/notifier.py의 형식을 따름)
    test_items = [
        {
            "org": "테스트 기관 A",
            "title": "2026년 인공지능 고도화 사업 공고 (채널 멘션 테스트)",
            "budget": 150000000,
            "url": "https://www.example.com/post/1"
        },
        {
            "org": "디지털 진흥원",
            "title": "클라우드 인프라 구축 용역 (채널 멘션 테스트)",
            "budget": 50000000,
            "url": "https://www.example.com/post/2"
        }
    ]

    print(f"[*] 슬랙 알림 전송 시도 중... (URL: {webhook_url[:40]}...)")
    
    try:
        # src/notifier.py의 함수 호출 (이제 내부에서 <!channel>을 포함합니다)
        send_slack_notification(webhook_url, test_items)
        print("[+] 전송 완료! 슬랙 채널을 확인해 보세요.")
    except Exception as e:
        print(f"[!] 전송 실패: {e}")

if __name__ == "__main__":
    test_slack()