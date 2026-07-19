# YES24 오픈 API 레퍼런스

> **Base URL**: `https://apis.yes24.com`
> **인증 방식**: `X-Api-Key` 헤더 (키 발급: [예스24 개발자센터](https://developers.yes24.com))
> **Content-Type**: `application/json` (응답은 camelCase)

기계가 읽을 수 있는 전체 명세는 [openapi/yes24-openapi-v1.json](../openapi/yes24-openapi-v1.json), 오류 코드 상세는 [error-codes.md](error-codes.md) 를 참고하세요.

---

## 목차

- [인증](#1-인증)
- [카테고리](#2-카테고리-category)
- [상품](#3-상품-goods)
- [Excel 다운로드](#4-excel-다운로드-export)
- [공통 응답 모델](#공통-응답-모델)

---

## 1. 인증

모든 요청에 발급받은 API 키를 `X-Api-Key` 헤더로 전달합니다.

```bash
curl -H "X-Api-Key: {발급받은키}" "https://apis.yes24.com/v1/goods/itemList?query=클린 코드"
```

| 상황 | 응답 |
|---|---|
| 헤더 누락 | `401` / `AUTH_001` |
| 유효하지 않은 키 | `401` / `AUTH_002` |

**요청 한도**: 초당 5회, 일 5,000회. 현재 잔여량은 응답의 `X-RateLimit-*` 헤더로 확인할 수 있으며,
초과 시 `429` 와 `Retry-After` 헤더(재시도 대기 초)가 반환됩니다.

---

## 2. 카테고리 (Category)

> **Base Path**: `/v1/category` · 인증 필요(`X-Api-Key`)

### 2.1 카테고리 목록 조회

예스24의 분야별 카테고리 목록을 조회합니다. 베스트셀러·신상품 조회의 `categoryId` 값으로 사용합니다.

- **메서드**: `GET` / **경로**: `/v1/category/list`
- 요청 파라미터: 없음

**200 OK**

```json
{
  "success": true,
  "message": "성공",
  "data": {
    "meta": { "...": "..." },
    "data": [
      {
        "categoryId": "001",
        "categoryName": "국내도서",
        "categoryFullPath": "국내도서",
        "categoryUrl": "https://yes24.com/product/category/display/001"
      }
    ]
  },
  "errorCode": null
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `categoryId` | string | 카테고리 ID |
| `categoryName` | string | 카테고리 명 |
| `categoryFullPath` | string | 카테고리 전체 경로 |
| `categoryUrl` | string | 카테고리 페이지 URL |

**404** — `CATEGORY_001`

---

### 2.2 베스트셀러(실시간) 조회

지정된 카테고리의 실시간 베스트셀러 목록(상위 100건)을 조회합니다.

- **메서드**: `GET` / **경로**: `/v1/category/bestsellerRealtime`

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `categoryId` | string | ✅ | — | 카테고리 ID |
| `detail` | string | ❌ | `N` | 상세정보 포함 여부 (`Y`: 전체정보, `N`: 간단정보) |

**400** — `categoryId` 미입력 시 `PARAM_001` · **404** — `BEST_001`

---

### 2.3 베스트셀러(종합) 조회

종합 집계 기준의 베스트셀러 목록을 조회합니다. 성별·연령 필터를 지원합니다.

- **메서드**: `GET` / **경로**: `/v1/category/bestseller`

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `categoryId` | string | ✅ | — | 카테고리 ID |
| `sex` | string | ❌ | `A` | 성별 필터 — `A`(전체), `M`(남성), `F`(여성) |
| `age` | integer | ❌ | `255` | 연령 필터 — `255`(전체), `10`, `20`, `30`, `40`, `50`, `60`(60대 이상) |
| `page` | integer | ❌ | `1` | 페이지 번호 |
| `pageSize` | integer | ❌ | `20` | 페이지 크기 (1~100) |
| `detail` | string | ❌ | `N` | 상세정보 포함 여부 (`Y`/`N`) |

**400** — `PARAM_001` · **404** — `BEST_001`

---

### 2.4 베스트셀러(일별) 조회

지정한 날짜 기준의 베스트셀러 목록을 조회합니다. `date` 를 생략하면 어제 날짜 기준입니다.

- **메서드**: `GET` / **경로**: `/v1/category/bestsellerDaily`

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `categoryId` | string | ✅ | — | 카테고리 ID |
| `date` | string | ❌ | 어제 | 조회 기준일 (`yyyy-MM-dd`) |
| `sex` | string | ❌ | `A` | 성별 필터 — `A`, `M`, `F` |
| `age` | integer | ❌ | `255` | 연령 필터 — `255`, `10`~`60` |
| `page` | integer | ❌ | `1` | 페이지 번호 |
| `pageSize` | integer | ❌ | `20` | 페이지 크기 (1~100) |
| `detail` | string | ❌ | `N` | 상세정보 포함 여부 (`Y`/`N`) |

**400** — `PARAM_001`(categoryId 누락), `PARAM_002`(date 형식 오류) · **404** — `BEST_001`

---

### 2.5 베스트셀러(월별) 조회

지정한 날짜가 속한 연월 기준의 베스트셀러 목록을 조회합니다. `date` 를 생략하면 어제 날짜 기준입니다.

- **메서드**: `GET` / **경로**: `/v1/category/bestsellerMonthly`
- 파라미터: [일별 베스트셀러](#24-베스트셀러일별-조회)와 동일

**400** — `PARAM_001`, `PARAM_002` · **404** — `BEST_001`

---

### 2.6 베스트셀러(특가) 조회

특가 집계 기준의 베스트셀러 목록을 조회합니다.

- **메서드**: `GET` / **경로**: `/v1/category/bestsellerDeal`

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `categoryId` | string | ✅ | — | 카테고리 ID |
| `page` | integer | ❌ | `1` | 페이지 번호 |
| `pageSize` | integer | ❌ | `20` | 페이지 크기 (1~100) |
| `detail` | string | ❌ | `N` | 상세정보 포함 여부 (`Y`/`N`) |

**400** — `PARAM_001` · **404** — `BEST_001`

---

### 2.7 스테디셀러 조회

꾸준히 판매되는 스테디셀러 목록을 조회합니다.

- **메서드**: `GET` / **경로**: `/v1/category/bestsellerSteady`
- 파라미터: [특가 베스트셀러](#26-베스트셀러특가-조회)와 동일

**400** — `PARAM_001` · **404** — `BEST_001`

---

### 2.8 신상품 조회

특정 카테고리의 신상품 목록을 조회합니다. 정렬 옵션을 지원합니다.

- **메서드**: `GET` / **경로**: `/v1/category/newproduct`

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `categoryId` | string | ✅ | — | 카테고리 ID |
| `sort` | string | ❌ | `RegDate` | 정렬 코드 — `RegDate`(등록일순), `Sales`(판매량순), `New`(신상품순), `LowPrice`(최저가순), `HighPrice`(최고가순), `Name`(상품명순) |
| `page` | integer | ❌ | `1` | 페이지 번호 |
| `pageSize` | integer | ❌ | `20` | 페이지 크기 (1~100) |
| `detail` | string | ❌ | `N` | 상세정보 포함 여부 (`Y`/`N`) |

**400** — `PARAM_001`(categoryId 누락), `PARAM_005`(잘못된 sort 값) · **404** — `NEW_001`

---

### 2.9 주목할 신상품 조회

편집 기준으로 선별된 주목할 신상품 목록을 조회합니다.

- **메서드**: `GET` / **경로**: `/v1/category/newproductAttention`
- 파라미터: [신상품 조회](#28-신상품-조회)와 동일

**400** — `PARAM_001`, `PARAM_005` · **404** — `ATTN_001`

---

## 3. 상품 (Goods)

> **Base Path**: `/v1/goods` · 인증 필요(`X-Api-Key`)

### 3.1 상품 검색

검색어로 상품 목록을 페이징 조회합니다.

- **메서드**: `GET` / **경로**: `/v1/goods/itemList`

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `query` | string | ✅ | — | 검색어 |
| `category` | string | ❌ | `ALL` | 검색 카테고리 — `ALL`(전체), `BOOK`(국내도서), `FOREIGN`(외국도서), `EBOOK`(전자책), `MUSIC`(음반), `DVD` |
| `sort` | string | ❌ | `DEFAULT` | 정렬 방식 — `DEFAULT`(인기도순), `RELATION`(정확도순), `RECENT`(신상품순), `REG_DTS`(등록일순) |
| `page` | integer | ❌ | `1` | 페이지 번호 |
| `pageSize` | integer | ❌ | `20` | 페이지 크기 |
| `detail` | string | ❌ | `N` | 상세정보 포함 여부 (`Y`/`N`) |

**400** — `PARAM_003`(query 누락) · **404** — `SEARCH_001`

---

### 3.2 상품 상세 조회

상품 번호(ItemId) 또는 ISBN13으로 상품 상세 정보를 조회합니다.

- **메서드**: `GET` / **경로**: `/v1/goods/itemDetail`

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `searchType` | string | ❌ | `ISBN13` | 검색 유형 — `ISBN13`, `ItemId` |
| `query` | string | ✅ | — | ISBN13 값(13자리) 또는 상품 번호 |
| `detail` | string | ❌ | `N` | 상세정보 포함 여부 (`Y`/`N`) |

**400** — `PARAM_003`(query 누락), `PARAM_004`(잘못된 값) · **404** — `GOODS_002`(ISBN13 미매칭), `GOODS_001`(상품 없음)

---

### 3.3 상품 목차 조회

상품의 목차 정보를 조회합니다.

- **메서드**: `GET` / **경로**: `/v1/goods/content`

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `searchType` | string | ❌ | `ISBN13` | 검색 유형 — `ISBN13`, `ItemId` |
| `query` | string | ✅ | — | ISBN13 값 또는 상품 번호 |

**200 OK**

```json
{
  "success": true,
  "message": "성공",
  "data": {
    "meta": { "...": "..." },
    "data": {
      "itemId": 12345678,
      "contents": "1장. 서론\n2장. 본론\n..."
    }
  },
  "errorCode": null
}
```

**400** — `PARAM_003`, `PARAM_004` · **404** — `GOODS_002`, `GOODS_001`(목차 없음)

---

### 3.4 작가 기본 정보 조회

상품 번호 또는 ISBN13으로 작가의 기본 정보를 조회합니다.

- **메서드**: `GET` / **경로**: `/v1/goods/author`

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `searchType` | string | ❌ | `ISBN13` | 검색 유형 — `ISBN13`, `ItemId` |
| `query` | string | ✅ | — | ISBN13 값 또는 상품 번호 |

**200 OK**

```json
{
  "success": true,
  "message": "성공",
  "data": {
    "meta": { "...": "..." },
    "data": {
      "authorId": 100001,
      "author": "홍길동",
      "authorType": "저자",
      "birthDate": "1970-01-01",
      "deathDate": "",
      "debutTitle": "첫 번째 작품",
      "details": "작가 소개 내용...",
      "link": "https://yes24.com/product/author/100001"
    }
  },
  "errorCode": null
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `authorId` | integer | 작가 번호 |
| `author` | string | 작가명 |
| `authorType` | string | 작가 구분 |
| `birthDate` | string | 생년월일 |
| `deathDate` | string | 사망일 |
| `debutTitle` | string | 데뷔작 제목 |
| `details` | string | 작가 소개 |
| `link` | string | 작가 페이지 URL |

**400** — `PARAM_003`, `PARAM_004` · **404** — `GOODS_002`, `AUTHOR_404`(작가 정보 없음)

---

## 4. Excel 다운로드 (export)

카테고리의 모든 조회 API는 결과를 `.xlsx` 파일로 내려받는 `/export` 변형을 제공합니다.
파라미터는 원본 API와 동일하며(`detail` 제외), 응답 Content-Type 은
`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` 입니다.

```
GET /v1/category/list/export
GET /v1/category/bestsellerRealtime/export
GET /v1/category/bestseller/export
GET /v1/category/bestsellerDaily/export
GET /v1/category/bestsellerMonthly/export
GET /v1/category/bestsellerDeal/export
GET /v1/category/bestsellerSteady/export
GET /v1/category/newproduct/export
GET /v1/category/newproductAttention/export
```

---

## 공통 응답 모델

### ApiResponse\<T\>

모든 API의 최상위 응답 래퍼입니다.

| 필드 | 타입 | 설명 |
|------|------|------|
| `success` | boolean | 요청 성공 여부 |
| `message` | string | 응답 메시지 |
| `data` | T | 응답 데이터 (실패 시 null) |
| `errorCode` | string? | 오류 코드 (성공 시 null) |

### PagedResult\<T\> — 목록 응답

상품 검색·베스트셀러·신상품 등 목록 응답의 `data` 구조입니다.

| 필드 | 타입 | 설명 |
|------|------|------|
| `meta` | ResponseMeta | 응답 메타 정보 |
| `items` | T[] | 아이템 목록 |
| `currentPage` | integer | 현재 페이지 번호 |
| `pageSize` | integer | 페이지 크기 |
| `totalCount` | integer | 전체 데이터 수 |

### DataWithMeta\<T\> — 단건 응답

카테고리 목록·목차·작가 정보 응답의 `data` 구조입니다. **내부 필드 이름도 `data`** 라는 점에 유의하세요 (`data.data`).

| 필드 | 타입 | 설명 |
|------|------|------|
| `meta` | ResponseMeta | 응답 메타 정보 |
| `data` | T | 실제 데이터 |

### ResponseMeta

| 필드 | 타입 | 설명 |
|------|------|------|
| `apiTitle` | string | API 제목 |
| `apiLink` | string | 요청 URL |
| `logoUrl` | string | YES24 로고 URL |
| `pubDate` | string | 응답 일시 (ISO 8601, KST) |
| `query` | string | 요청 쿼리 문자열 |
| `version` | string | API 버전 |

### GoodsSimpleInfo (detail=N 기본값)

| 필드 | 타입 | 설명 |
|------|------|------|
| `sortOrder` | integer | 순서 (베스트셀러 순위) |
| `itemId` | integer | 상품 번호 |
| `title` | string | 상품 제목 |
| `author` | string | 저자 |
| `goodsType` | string | 상품 유형 |
| `goodsSortNm` | string | 상품 분류명 |
| `adultYn` | string | 성인물 여부 (`Y`/`N`) |
| `publisher` | string | 출판사 |
| `isbn10` | string | ISBN10 |
| `isbn13` | string | ISBN13 |
| `shopPrice` | decimal | 정가 |
| `salePrice` | decimal | 판매가 |
| `publishDate` | string | 출간일 |
| `itemStatus` | string | 판매 상태 |
| `cover` | string | 표지 이미지 URL |
| `link` | string | 상품 페이지 URL |
| `upDown` | integer? | 순위 등락 (베스트셀러 응답) |
| `contentDetail` | object? | 상품 소개·요약·목차 (제공 시) |

### GoodsInfo (detail=Y 전체정보)

GoodsSimpleInfo 의 모든 필드에 아래 필드가 추가됩니다.

| 필드 | 타입 | 설명 |
|------|------|------|
| `subTitle` | string | 부제목 |
| `originalTitle` | string? | 원제 |
| `originalTranslation` | string? | 번역서 여부 |
| `pages` | integer? | 페이지 수 |
| `weight`/`width`/`height`/`length` | integer? | 무게(g)·크기(mm) |
| `itemFormat` | string | 판형 |
| `yesPoint` | integer? | YES 포인트 |
| `salePoint` | integer? | 판매지수 |
| `fixedBookPriceYn` | string | 도서정가제 여부 |
| `starScore` | double | 별점 (리뷰 평균) |
| `mobileLink` | string | 모바일 상품 페이지 URL |
| `ebookId` / `eBookLink` | integer? / string | 연계 eBook 정보 |
| `series` | array | 시리즈 목록 (`seriesId`, `seriesName`) |

전체 필드 목록은 [openapi/yes24-openapi-v1.json](../openapi/yes24-openapi-v1.json) 의 `GoodsInfo` 스키마를 참고하세요.

---

## 오류 코드

전체 오류 코드와 해결 방법은 [error-codes.md](error-codes.md) 를 참고하세요.
