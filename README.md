# YES24 오픈 API 공식 샘플

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

예스24 오픈 API의 공식 샘플 저장소입니다. 도서 검색·베스트셀러·신상품 API를 활용하는
실행 가능한 예제와 OpenAPI 명세, Postman Collection 을 제공합니다.

- **API 키 발급·문서·이용 현황**: [예스24 개발자센터](https://developers.yes24.com)
- **API 서버**: `https://apis.yes24.com`

## 제공 API 한눈에 보기

| 분류 | 엔드포인트 | 설명 |
|---|---|---|
| 상품 | `GET /v1/goods/itemList` | 도서·상품 검색 (카테고리·정렬·페이징) |
| 상품 | `GET /v1/goods/itemDetail` | 상품 상세 (ISBN13 또는 상품 번호) |
| 상품 | `GET /v1/goods/content` | 목차 조회 |
| 상품 | `GET /v1/goods/author` | 작가 정보 조회 |
| 카테고리 | `GET /v1/category/list` | 카테고리 목록 |
| 카테고리 | `GET /v1/category/bestseller` | 종합 베스트셀러 (성별·연령 필터) |
| 카테고리 | `GET /v1/category/bestsellerRealtime` `…Daily` `…Monthly` `…Deal` `…Steady` | 실시간·일별·월별·특가·스테디셀러 |
| 카테고리 | `GET /v1/category/newproduct` `…Attention` | 신상품·주목할 신상품 |
| 공통 | 위 카테고리 API 의 `/export` 변형 | 결과를 Excel(.xlsx)로 다운로드 |

전체 파라미터와 응답 필드는 [docs/api-reference.md](docs/api-reference.md) 참고.

## 시작하기

```bash
# 1. 개발자센터(https://developers.yes24.com)에서 API 키 발급
# 2. X-Api-Key 헤더로 호출
curl -H "X-Api-Key: {발급받은키}" \
  "https://apis.yes24.com/v1/goods/itemList?query=클린 코드&pageSize=3"
```

처음이라면 [5분 시작 가이드](docs/getting-started.md)를 따라 해 보세요.

## 저장소 구성

| 경로 | 내용 | 필요 런타임 |
|---|---|---|
| [samples/dotnet-book-search](samples/dotnet-book-search) | 도서 검색 콘솔 앱 (외부 패키지 0개) | .NET 10 SDK |
| [samples/javascript-bestseller-widget](samples/javascript-bestseller-widget) | 임베드형 베스트셀러 위젯 + 프록시 (키 없이 데모 실행 가능) | Node.js 18+ |
| [samples/python-book-analysis](samples/python-book-analysis) | 베스트셀러 200건 수집·분석 (pandas, 노트북 포함) | Python 3.10+ |
| [openapi/](openapi) | OpenAPI 3.0 명세 (`yes24-openapi-v1.json`) | — |
| [postman/](postman) | Postman Collection + Environment | Postman |
| [docs/](docs) | 시작 가이드 · API 레퍼런스 · 오류 코드 | — |

모든 샘플은 클론 후 5분 내 실행을 목표로 하며, 공통 환경변수를 사용합니다.

| 환경변수 | 설명 |
|---|---|
| `YES24_API_KEY` | 개발자센터에서 발급한 API 키 (위젯 샘플은 없으면 데모 모드) |
| `YES24_API_BASE_URL` | 기본 `https://apis.yes24.com` — 보통 변경할 필요 없음 |

## OpenAPI 명세와 Postman

- **OpenAPI**: [openapi/yes24-openapi-v1.json](openapi/yes24-openapi-v1.json) — Swagger UI·코드 생성기·API 클라이언트에서 import 해 사용하세요.
- **Postman**: [postman/](postman) 의 Collection 과 Environment 를 모두 import 한 뒤, Environment 의 `apiKey` 변수에 발급 키를 넣으면 바로 호출할 수 있습니다. (Bruno 등 Collection 호환 도구에서도 사용 가능)

## 요청 한도와 오류

- **한도**: 초당 5회, 일 5,000회 (키 기준, 자정 KST 초기화)
- 잔여량은 `X-RateLimit-*` 응답 헤더로 확인, 초과 시 `429` + `Retry-After`(초) 반환
- 모든 오류는 `{ "success": false, "errorCode": "...", "message": "..." }` 형식 — 전체 목록은 [docs/error-codes.md](docs/error-codes.md)

## 자주 묻는 질문

**Q. 브라우저(프런트엔드)에서 API를 직접 호출해도 되나요?**
안 됩니다. CORS 정책상 차단되며, 무엇보다 브라우저 코드에 넣은 API 키는 누구나 볼 수 있습니다.
[위젯 샘플](samples/javascript-bestseller-widget)처럼 자체 서버(프록시)를 경유하세요.

**Q. API 키를 실수로 공개 저장소에 올렸어요.**
개발자센터에서 즉시 키를 폐기하고 재발급하세요. 공개된 키는 회수해도 이미 노출된 것으로 간주해야 합니다.

**Q. 검색 결과가 404(SEARCH_001)로 와요.**
오류가 아니라 "결과 없음" 응답입니다. 다른 검색어로 시도하세요.

## 문의

이 저장소는 읽기 전용으로 운영되며 **Issues·Pull Request 를 받지 않습니다**.
버그 제보·기능 요청·사용 문의는 [예스24 개발자센터](https://developers.yes24.com)의 문의 채널을 이용해 주세요.

## 라이선스

- 이 저장소의 **샘플 코드**는 [MIT License](LICENSE) 로 자유롭게 사용할 수 있습니다.
- **API 및 API 로 제공되는 데이터**는 예스24 오픈 API 이용약관을 따릅니다.
