# .NET 10 도서 검색 샘플

예스24 오픈 API의 도서 검색(`GET /v1/goods/itemList`)을 호출하는 콘솔 앱입니다.
외부 NuGet 패키지 없이 `HttpClient` + `System.Net.Http.Json` 만 사용합니다.

## 필요 사항

- [.NET 10 SDK](https://dotnet.microsoft.com/download)
- 예스24 개발자센터([developers.yes24.com](https://developers.yes24.com))에서 발급한 API 키

## 실행 방법

```powershell
# 1. API 키 설정 (PowerShell 기준)
$env:YES24_API_KEY = "발급받은키"

# 2. 실행 — 첫 번째 인자는 검색어, 두 번째 인자(선택)는 카테고리
dotnet run -- "클린 코드"
dotnet run -- "해리 포터" BOOK
```

- 카테고리: `ALL`(기본), `BOOK`(국내도서), `FOREIGN`(외국도서), `EBOOK`, `MUSIC`, `DVD`

## 실행 결과 예시

```
"클린 코드" 검색 결과 총 128건 중 상위 10건
────────────────────────────────────────────────────────────
 1. 클린 코드
    로버트 C. 마틴 | 인사이트 | 2013-12-24
    정가 33,000원 → 판매가 29,700원 | ISBN13 9788966260959
    https://www.yes24.com/product/goods/...
```

## 코드에서 볼 것

| 내용 | 위치 |
|---|---|
| `X-Api-Key` 헤더 인증 | `http.DefaultRequestHeaders.Add("X-Api-Key", ...)` |
| 공통 응답 래퍼 역직렬화 | `ApiResponse<PageData<Book>>` record 3개 |
| 요청 한도(429) 처리 | `Retry-After` 헤더 안내 후 종료 |
| 오류 응답 처리 | `success=false` 시 `errorCode`/`message` 출력 |

## 환경변수

| 이름 | 필수 | 설명 |
|---|---|---|
| `YES24_API_KEY` | O | 개발자센터에서 발급한 API 키 |
| `YES24_API_BASE_URL` | X | 기본 `https://apis.yes24.com` (테스트 서버로 전환 시에만 변경) |
