# -*- coding: utf-8 -*-
"""예스24 오픈 API 베스트셀러 데이터 분석 예제.

수집: GET /v1/category/bestseller (국내도서, 100건 x 2페이지 = 200건)
분석: 1) 판매가 분포와 할인율  2) 출판사 TOP 10  3) 출간 연도 분포
결과: output/ 폴더에 차트 PNG 3개 저장 + 콘솔 요약 출력

실행 전 환경변수 YES24_API_KEY 설정 필요 (발급: https://developers.yes24.com)
"""
import os
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # 화면 없이 PNG 저장만 수행
import matplotlib.pyplot as plt
import pandas as pd
import requests

API_BASE = os.environ.get("YES24_API_BASE_URL", "https://apis.yes24.com")
API_KEY = os.environ.get("YES24_API_KEY")
CATEGORY_ID = "001"  # 국내도서
PAGE_SIZE = 100
PAGES = 2
OUT_DIR = Path(__file__).parent / "output"


def set_korean_font() -> None:
    """matplotlib 한글 깨짐 방지 — OS별 기본 한글 폰트 지정."""
    if sys.platform.startswith("win"):
        plt.rcParams["font.family"] = "Malgun Gothic"
    elif sys.platform == "darwin":
        plt.rcParams["font.family"] = "AppleGothic"
    else:
        plt.rcParams["font.family"] = "NanumGothic"  # 리눅스는 나눔고딕 설치 필요
    plt.rcParams["axes.unicode_minus"] = False


def fetch_bestsellers() -> list[dict]:
    """베스트셀러 목록 수집. 요청 한도(5회/초)를 지키고 429 응답 시 Retry-After 만큼 대기."""
    if not API_KEY:
        sys.exit("환경변수 YES24_API_KEY 를 설정하세요. 발급: https://developers.yes24.com")

    session = requests.Session()
    session.headers["X-Api-Key"] = API_KEY

    rows: list[dict] = []
    page = 1
    while page <= PAGES:
        resp = session.get(
            f"{API_BASE}/v1/category/bestseller",
            params={"categoryId": CATEGORY_ID, "page": page, "pageSize": PAGE_SIZE},
            timeout=10,
        )
        if resp.status_code == 429:  # 요청 한도 초과 — 안내된 시간만큼 기다렸다가 같은 페이지 재시도
            wait = int(resp.headers.get("Retry-After") or 1)
            print(f"요청 한도 초과(429) — {wait}초 대기 후 재시도합니다.")
            time.sleep(wait)
            continue

        payload = resp.json()
        if not payload.get("success"):
            sys.exit(f"API 오류 [{payload.get('errorCode')}] {payload.get('message')}")

        items = payload["data"]["items"]
        rows.extend(items)
        print(f"{page}페이지 수집: {len(items)}건 (누적 {len(rows)}건)")

        page += 1
        time.sleep(0.25)  # 초당 5회 제한 준수

    return rows


def build_dataframe(rows: list[dict]) -> pd.DataFrame:
    df = pd.json_normalize(rows)
    df["shopPrice"] = pd.to_numeric(df["shopPrice"], errors="coerce")
    df["salePrice"] = pd.to_numeric(df["salePrice"], errors="coerce")
    df["publishYear"] = pd.to_datetime(df["publishDate"], errors="coerce").dt.year
    priced = df["shopPrice"] > 0
    df.loc[priced, "discountRate"] = (
        (df.loc[priced, "shopPrice"] - df.loc[priced, "salePrice"]) / df.loc[priced, "shopPrice"] * 100
    ).round(1)
    return df


def chart_price(df: pd.DataFrame) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    ax1.hist(df["salePrice"].dropna() / 1000, bins=15, color="#4c78a8", edgecolor="white")
    ax1.set_title("판매가 분포")
    ax1.set_xlabel("판매가 (천 원)")
    ax1.set_ylabel("도서 수")
    ax2.hist(df["discountRate"].dropna(), bins=12, color="#f58518", edgecolor="white")
    ax2.set_title("할인율 분포")
    ax2.set_xlabel("할인율 (%)")
    ax2.set_ylabel("도서 수")
    fig.suptitle(f"베스트셀러 가격 분석 (표본 {len(df)}건)")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "price_distribution.png", dpi=150)
    plt.close(fig)


def chart_publishers(df: pd.DataFrame) -> pd.Series:
    top = df["publisher"].value_counts().head(10).sort_values()
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.barh(top.index, top.values, color="#4c78a8")
    ax.set_title("베스트셀러 최다 진입 출판사 TOP 10")
    ax.set_xlabel("도서 수")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "publisher_top10.png", dpi=150)
    plt.close(fig)
    return top


def chart_publish_year(df: pd.DataFrame) -> None:
    counts = df["publishYear"].dropna().astype(int).value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.bar(counts.index.astype(str), counts.values, color="#54a24b")
    ax.set_title("베스트셀러 출간 연도 분포")
    ax.set_xlabel("출간 연도")
    ax.set_ylabel("도서 수")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "publish_year.png", dpi=150)
    plt.close(fig)


def main() -> None:
    set_korean_font()
    OUT_DIR.mkdir(exist_ok=True)

    df = build_dataframe(fetch_bestsellers())

    chart_price(df)
    top_publishers = chart_publishers(df)
    chart_publish_year(df)

    up = int((df["upDown"] > 0).sum())
    down = int((df["upDown"] < 0).sum())
    same = int((df["upDown"] == 0).sum())

    print()
    print("=== 분석 요약 ===")
    print(f"표본           : 국내도서 베스트셀러 {len(df)}건")
    print(f"평균 판매가    : {df['salePrice'].mean():,.0f}원 (중앙값 {df['salePrice'].median():,.0f}원)")
    print(f"평균 할인율    : {df['discountRate'].mean():.1f}%")
    print(f"최다 출판사    : {top_publishers.idxmax()} ({top_publishers.max()}권)")
    print(f"순위 등락      : 상승 {up} / 하락 {down} / 유지 {same}")
    print(f"차트 저장 위치 : {OUT_DIR}")


if __name__ == "__main__":
    main()
