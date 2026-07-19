# 5분 시작 가이드

## 1. API 키 발급

1. [예스24 개발자센터](https://developers.yes24.com)에 로그인합니다.
2. API 키 발급 메뉴에서 키를 발급받습니다.
3. 발급된 키는 **외부에 노출되지 않게** 보관하세요. (소스 코드·공개 저장소에 넣지 말 것)

## 2. 첫 호출

발급받은 키를 `X-Api-Key` 헤더에 넣어 도서를 검색해 봅니다.

```bash
curl -H "X-Api-Key: {발급받은키}" \
  "https://apis.yes24.com/v1/goods/itemList?query=클린 코드&pageSize=3"
```

PowerShell 이라면:

```powershell
Invoke-RestMethod -Headers @{ "X-Api-Key" = "발급받은키" } `
  -Uri "https://apis.yes24.com/v1/goods/itemList?query=클린 코드&pageSize=3"
```

## 3. 응답 읽기

```json
{
  "success": true,
  "message": "성공",
  "data": {
    "meta": { "apiTitle": "상품 검색", "version": "v1" },
    "items": [
      {
        "itemId": 11681152,
        "title": "클린 코드",
        "author": "로버트 C. 마틴",
        "publisher": "인사이트",
        "isbn13": "9788966260959",
        "shopPrice": 33000,
        "salePrice": 29700,
        "cover": "https://image.yes24.com/...",
        "link": "https://www.yes24.com/..."
      }
    ],
    "currentPage": 1,
    "pageSize": 3,
    "totalCount": 128
  },
  "errorCode": null
}
```

- 모든 응답은 `{ success, message, data, errorCode }` 로 감싸져 있습니다.
- 목록 응답의 `data` 안에는 `items[]` 와 페이징 정보가 있습니다.
- 실패 시 `success=false` 와 함께 [오류 코드](error-codes.md)가 반환됩니다.

## 4. 요청 한도 확인

응답 헤더로 잔여 호출량을 확인할 수 있습니다.

| 헤더 | 의미 |
|---|---|
| `X-RateLimit-Limit-Second` / `X-RateLimit-Remaining-Second` | 초당 한도(5회) / 잔여 |
| `X-RateLimit-Limit-Day` / `X-RateLimit-Remaining-Day` | 일일 한도(5,000회) / 잔여 |
| `Retry-After` | 429 응답 시 재시도까지 대기 초 |

## 5. 다음 단계

- [API 레퍼런스](api-reference.md) — 전체 엔드포인트·파라미터·응답 필드
- [samples/](../samples) — .NET·JavaScript·Python·MCP 실행 가능한 샘플 4종
- [postman/](../postman) — Postman Collection 으로 바로 호출해 보기
