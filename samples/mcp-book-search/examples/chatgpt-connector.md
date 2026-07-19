# ChatGPT 커넥터 연결 방법

ChatGPT 의 MCP 커넥터는 **공개 HTTPS URL 의 원격 MCP 서버만** 지원합니다.
(Claude Desktop 처럼 로컬 stdio 프로세스를 직접 실행하는 방식은 지원하지 않습니다.)

## 1. HTTP 모드로 서버 실행

```powershell
$env:YES24_API_KEY = "발급받은키"
python server.py --http
# → http://127.0.0.1:8000/mcp (streamable HTTP)
```

## 2. 공개 HTTPS URL 확보

테스트라면 터널링 도구로 임시 URL을 만들 수 있습니다.

```powershell
ngrok http 8000
# 발급된 https://xxxx.ngrok-free.app 을 사용
```

실서비스라면 HTTPS 를 제공하는 서버/클라우드에 배포하세요.

## 3. ChatGPT 에 커넥터 등록

1. ChatGPT **설정 → 커넥터(Connectors)** 로 이동
2. 고급 설정에서 **개발자 모드(Developer mode)** 활성화 (커넥터 직접 추가에 필요)
3. **커넥터 추가** 에서 MCP 서버 URL 입력: `https://xxxx.ngrok-free.app/mcp`
4. 대화에서 커넥터를 활성화하고 질문:

```
예스24에서 "클린 코드"라는 책 찾아줘
```

## 보안 주의

- API 키는 서버 환경변수에만 있고 ChatGPT 에는 전달되지 않습니다.
- 다만 **URL 을 아는 누구나 이 서버를 통해 여러분의 키로 API 를 호출할 수 있습니다.**
  터널 URL 은 테스트 후 즉시 종료하고, 상시 운영 시에는 인증(예: 리버스 프록시의 토큰 검사)을 앞단에 두세요.
