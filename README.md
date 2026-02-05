# Market Notify (공공기관 공고 알림이)

나라장터(G2B) API를 호출하여 특정 키워드와 지역의 공고를 수집하고 Slack으로 알림을 보내는 AWS Lambda 기반 애플리케이션입니다.

## 주요 기능

- **다중 키워드 및 지역 검색**: 설정된 키워드와 지역 코드의 모든 조합으로 공고를 검색합니다.
- **KST 기준 조회**: 한국 시간 기준 전날(00:00~23:59)의 공고를 수집합니다.
- **Slack 알림**: 수집된 공고의 제목, 예산, 상세 URL 등을 Slack 채널로 전송합니다.
- **서버리스 아키텍처**: AWS Lambda와 EventBridge를 사용하여 저비용으로 자동화된 스케줄링이 가능합니다.

## 프로젝트 구조

- `handler.py`: AWS Lambda의 Entry Point 로직
- `src/api.py`: 공공 데이터 API 호출 모듈
- `src/processor.py`: 데이터 정규화(Normalization) 모듈
- `src/notifier.py`: Slack Webhook 알림 모듈
- `src/utils.py`: 설정 로드 및 로깅 유틸리티

## 환경 변수 설정

배포 시 다음 환경 변수를 AWS Lambda 또는 `.env`에 설정해야 합니다.

- `API_ENDPOINT`: 공공데이터포털 나라장터 서비스 엔드포인트
- `decoding`: 공공데이터포털에서 발급받은 일반 인증서(Decoding)
- `SLACK_WEBHOOK_URL`: 알림을 받을 Slack Webhook URL
- `INCLUDE_KEYWORDS`: (선택) 검색 키워드 (쉼표로 구분)
- `REGION_CODES`: (선택) 지역 코드 (쉼표로 구분, 지역표 참조)

## 로컬 테스트

```bash
python test.py
```
