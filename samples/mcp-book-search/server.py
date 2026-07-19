# -*- coding: utf-8 -*-
"""예스24 도서 검색 MCP 서버.

Claude·ChatGPT 같은 AI 어시스턴트가 예스24 오픈 API로 도서를 검색·조회할 수 있게 하는
MCP(Model Context Protocol) 서버 예제입니다. 공식 MCP Python SDK(FastMCP)를 사용합니다.

실행
  python server.py          # stdio 모드 — Claude Desktop·Claude Code 로컬 연결
  python server.py --http   # streamable HTTP 모드(127.0.0.1:8000/mcp) — 원격 연결·ChatGPT 커넥터용

환경변수
  YES24_API_KEY       (필수) 예스24 개발자센터(https://developers.yes24.com)에서 발급
  YES24_API_BASE_URL  (선택) 기본 https://apis.yes24.com
"""
import os
import sys
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

API_BASE = os.environ.get("YES24_API_BASE_URL", "https://apis.yes24.com")

mcp = FastMCP("yes24-books")

# 베스트셀러 종류 → 엔드포인트 매핑
BESTSELLER_PATHS = {
    "overall": "/v1/category/bestseller",
    "realtime": "/v1/category/bestsellerRealtime",
    "daily": "/v1/category/bestsellerDaily",
    "monthly": "/v1/category/bestsellerMonthly",
    "deal": "/v1/category/bestsellerDeal",
    "steady": "/v1/category/bestsellerSteady",
}

BOOK_FIELDS = (
    "sortOrder", "itemId", "title", "author", "publisher", "publishDate",
    "isbn13", "shopPrice", "salePrice", "upDown", "starScore", "pages", "link",
)


async def _call_api(path: str, params: dict[str, Any]) -> dict[str, Any]:
    """오픈 API 호출 공통 처리 — 인증 헤더 주입, 요청 한도·오류 응답을 메시지로 변환."""
    api_key = os.environ.get("YES24_API_KEY")
    if not api_key:
        return {"error": "환경변수 YES24_API_KEY 가 없습니다. https://developers.yes24.com 에서 키를 발급받아 설정하세요."}

    async with httpx.AsyncClient(base_url=API_BASE, timeout=10) as client:
        resp = await client.get(path, params=params, headers={"X-Api-Key": api_key})

    if resp.status_code == 429:
        retry = resp.headers.get("Retry-After", "1")
        return {"error": f"요청 한도 초과(429). {retry}초 후 다시 시도하세요."}

    payload = resp.json()
    if not payload.get("success"):
        return {"error": f"[{payload.get('errorCode')}] {payload.get('message')}"}
    return {"data": payload.get("data")}


def _slim(item: dict[str, Any]) -> dict[str, Any]:
    """LLM 이 읽기 좋게 필요한 필드만 추린다 (토큰 절약)."""
    return {k: item[k] for k in BOOK_FIELDS if item.get(k) is not None}


def _slim_items(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "totalCount": data.get("totalCount"),
        "currentPage": data.get("currentPage"),
        "books": [_slim(b) for b in data.get("items") or []],
    }


@mcp.tool()
async def search_books(
    query: str,
    category: str = "ALL",
    sort: str = "DEFAULT",
    page: int = 1,
    page_size: int = 10,
) -> dict[str, Any]:
    """예스24에서 도서를 검색한다.

    Args:
        query: 검색어 (도서명·저자명 등)
        category: ALL(전체)·BOOK(국내도서)·FOREIGN(외국도서)·EBOOK·MUSIC·DVD
        sort: DEFAULT(기본)·RELATION(정확도)·RECENT(신상품)·REG_DTS(등록일)
        page: 페이지 번호 (1부터)
        page_size: 페이지당 결과 수 (최대 100)
    """
    result = await _call_api(
        "/v1/goods/itemList",
        {"query": query, "category": category, "sort": sort, "page": page, "pageSize": page_size},
    )
    if "error" in result:
        return result
    return _slim_items(result["data"])


@mcp.tool()
async def get_book_detail(query: str, search_type: str = "ISBN13") -> dict[str, Any]:
    """도서 한 권의 상세 정보(부제·쪽수·평점·시리즈 등 확장 필드 포함)를 조회한다.

    Args:
        query: ISBN13(13자리) 또는 예스24 상품 번호
        search_type: ISBN13 또는 ItemId
    """
    result = await _call_api(
        "/v1/goods/itemDetail",
        {"searchType": search_type, "query": query, "detail": "Y"},
    )
    if "error" in result:
        return result
    items = result["data"].get("items") or []
    if not items:
        return {"error": "해당 도서를 찾을 수 없습니다."}
    book = dict(items[0])
    book.pop("contentDetail", None)  # 장문 필드는 목차 도구(get_book_toc)로 분리
    return {k: v for k, v in book.items() if v not in (None, "", [])}


@mcp.tool()
async def get_book_toc(query: str, search_type: str = "ISBN13") -> dict[str, Any]:
    """도서의 목차(차례)를 조회한다.

    Args:
        query: ISBN13(13자리) 또는 예스24 상품 번호
        search_type: ISBN13 또는 ItemId
    """
    result = await _call_api("/v1/goods/content", {"searchType": search_type, "query": query})
    if "error" in result:
        return result
    return result["data"].get("data") or {}


@mcp.tool()
async def get_author_info(query: str, search_type: str = "ISBN13") -> dict[str, Any]:
    """도서의 작가 정보(작가명·활동 분야·데뷔작·소개)를 조회한다.

    Args:
        query: ISBN13(13자리) 또는 예스24 상품 번호
        search_type: ISBN13 또는 ItemId
    """
    result = await _call_api("/v1/goods/author", {"searchType": search_type, "query": query})
    if "error" in result:
        return result
    return result["data"].get("data") or {}


@mcp.tool()
async def get_bestsellers(
    category_id: str = "001",
    kind: str = "overall",
    sex: str = "A",
    age: int = 255,
    date: str | None = None,
    page_size: int = 10,
) -> dict[str, Any]:
    """예스24 베스트셀러 목록을 조회한다.

    Args:
        category_id: 카테고리 ID (기본 001=국내도서, 전체 목록은 get_categories 참고)
        kind: overall(종합)·realtime(실시간)·daily(일별)·monthly(월별)·deal(특가)·steady(스테디셀러)
        sex: A(전체)·M(남성)·F(여성) — overall/daily/monthly 만 적용
        age: 255(전체)·10·20·30·40·50·60 — overall/daily/monthly 만 적용
        date: yyyy-MM-dd — daily/monthly 만 적용, 생략 시 어제 기준
        page_size: 결과 수 (최대 100)
    """
    path = BESTSELLER_PATHS.get(kind)
    if path is None:
        return {"error": f"kind 는 {', '.join(BESTSELLER_PATHS)} 중 하나여야 합니다."}

    params: dict[str, Any] = {"categoryId": category_id, "pageSize": page_size}
    if kind in ("overall", "daily", "monthly"):
        params |= {"sex": sex, "age": age}
    if kind in ("daily", "monthly") and date:
        params["date"] = date

    result = await _call_api(path, params)
    if "error" in result:
        return result
    return _slim_items(result["data"])


@mcp.tool()
async def get_categories() -> dict[str, Any]:
    """베스트셀러·신상품 조회에 사용할 수 있는 예스24 카테고리 목록을 조회한다."""
    result = await _call_api("/v1/category/list", {})
    if "error" in result:
        return result
    categories = result["data"].get("data") or []  # 카테고리 목록 응답은 data.data[]
    return {
        "categories": [
            {"categoryId": c.get("categoryId"), "categoryName": c.get("categoryName")}
            for c in categories
        ]
    }


if __name__ == "__main__":
    if "--http" in sys.argv:
        # 원격 연결용 — http://127.0.0.1:8000/mcp (ChatGPT 커넥터는 공개 HTTPS URL 필요)
        mcp.run(transport="streamable-http")
    else:
        mcp.run()  # stdio — Claude Desktop·Claude Code 로컬 연결
