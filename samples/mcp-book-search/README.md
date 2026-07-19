# ChatGPT·Claude용 도서 검색 MCP 서버

Claude·ChatGPT 같은 AI 어시스턴트가 예스24 오픈 API로 도서를 검색·조회할 수 있게 하는
**MCP(Model Context Protocol) 서버** 예제입니다.
공식 [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)의 FastMCP 를 사용한 단일 파일(`server.py`) 구성입니다.

연결하면 이렇게 쓸 수 있습니다.

> "예스24에서 클린 코드 검색해서 가장 싼 판 알려줘"
> "이번 주 국내도서 실시간 베스트셀러 요약해줘"
> "ISBN 9788966260959 목차 보여줘"

## 제공 도구 (6개)

| 도구 | 설명 | 매핑 엔드포인트 |
|---|---|---|
| `search_books` | 도서 검색 | `GET /v1/goods/itemList` |
| `get_book_detail` | 상세 정보 (쪽수·평점·시리즈 등) | `GET /v1/goods/itemDetail` |
| `get_book_toc` | 목차 조회 | `GET /v1/goods/content` |
| `get_author_info` | 작가 정보 | `GET /v1/goods/author` |
| `get_bestsellers` | 베스트셀러 (종합·실시간·일별·월별·특가·스테디) | `GET /v1/category/bestseller*` |
| `get_categories` | 카테고리 목록 | `GET /v1/category/list` |

## 준비

```powershell
pip install -r requirements.txt
$env:YES24_API_KEY = "발급받은키"   # 발급: https://developers.yes24.com
```

## 연결 방법 (클라이언트별)

| 클라이언트 | 방식 | 안내 문서 |
|---|---|---|
| Claude Desktop | stdio (로컬 실행) | [examples/claude_desktop_config.json](examples/claude_desktop_config.json) 을 `claude_desktop_config.json` 에 병합 |
| Claude Code | stdio (로컬 실행) | [examples/claude-code.md](examples/claude-code.md) |
| ChatGPT | 원격 HTTPS (`--http` 모드) | [examples/chatgpt-connector.md](examples/chatgpt-connector.md) |

## 직접 테스트 (MCP Inspector)

클라이언트 연결 전에 도구 노출을 확인하려면:

```powershell
npx @modelcontextprotocol/inspector python server.py
```

브라우저에 열리는 Inspector 에서 6개 도구가 보이고, `search_books` 를 실행해 결과가 오면 정상입니다.

## 환경변수

| 이름 | 필수 | 설명 |
|---|---|---|
| `YES24_API_KEY` | O | 개발자센터에서 발급한 API 키 (서버 측에만 보관) |
| `YES24_API_BASE_URL` | X | 기본 `https://apis.yes24.com` |
