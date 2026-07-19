# Claude Code 연결 방법

## 방법 1 — CLI 한 줄 등록

```bash
claude mcp add yes24-books -e YES24_API_KEY=발급받은키 -- python C:/path/to/yes24-openapi-samples/samples/mcp-book-search/server.py
```

- `-e` 로 환경변수를 전달하고, `--` 뒤에 서버 실행 명령을 적습니다.
- 경로는 클론한 위치의 **절대 경로**로 바꾸세요.

## 방법 2 — 프로젝트 공유 설정(.mcp.json)

프로젝트 루트에 `.mcp.json` 파일을 만들면 팀원과 설정을 공유할 수 있습니다.

```json
{
  "mcpServers": {
    "yes24-books": {
      "command": "python",
      "args": ["C:/path/to/yes24-openapi-samples/samples/mcp-book-search/server.py"],
      "env": {
        "YES24_API_KEY": "${YES24_API_KEY}"
      }
    }
  }
}
```

`${YES24_API_KEY}` 는 실행 환경의 환경변수를 참조하므로 **키를 파일에 직접 적지 않아도 됩니다**
(`.mcp.json` 을 저장소에 커밋할 때 키가 유출되지 않게 하는 방법입니다).

## 동작 확인

Claude Code 에서:

```
> 예스24에서 "클린 코드" 검색해줘
> 국내도서 실시간 베스트셀러 10권 보여줘
```

`search_books`, `get_bestsellers` 도구가 호출되면 정상 연결된 것입니다.
