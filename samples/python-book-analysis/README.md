# Python 도서 데이터 분석 예제

예스24 오픈 API로 **국내도서 베스트셀러 200건**을 수집해 pandas 로 분석하는 예제입니다.

- 판매가·할인율 분포 히스토그램
- 베스트셀러 최다 진입 출판사 TOP 10
- 출간 연도 분포 + 순위 등락(상승/하락/유지) 요약

같은 내용이 두 가지 형태로 있습니다.

| 파일 | 용도 |
|---|---|
| `bestseller_analysis.py` | 터미널 실행용 — `output/` 폴더에 차트 PNG 3개 저장 |
| `bestseller_analysis.ipynb` | Jupyter 노트북 — 셀 단위로 실행하며 차트를 바로 확인 |

## 실행 방법

```powershell
# 1. 의존성 설치
pip install -r requirements.txt

# 2. API 키 설정 (발급: https://developers.yes24.com)
$env:YES24_API_KEY = "발급받은키"

# 3-a. 스크립트 실행
python bestseller_analysis.py

# 3-b. 또는 노트북 실행
jupyter notebook bestseller_analysis.ipynb
```

## 코드에서 볼 것

- **요청 한도 준수** — 페이지 사이 `time.sleep(0.25)`(초당 5회 제한), 429 응답 시 `Retry-After` 헤더만큼 대기 후 재시도
- **응답 → DataFrame** — `pd.json_normalize(payload["data"]["items"])`
- **한글 차트** — OS별 폰트 지정(`Malgun Gothic`/`AppleGothic`/`NanumGothic`)으로 matplotlib 한글 깨짐 방지

## 환경변수

| 이름 | 필수 | 설명 |
|---|---|---|
| `YES24_API_KEY` | O | 개발자센터에서 발급한 API 키 |
| `YES24_API_BASE_URL` | X | 기본 `https://apis.yes24.com` |
