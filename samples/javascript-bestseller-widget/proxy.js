// 예스24 베스트셀러 위젯 프록시 서버 (Node.js 내장 모듈만 사용, npm install 불필요)
//
// 브라우저에서 apis.yes24.com 을 직접 호출할 수 없는 이유:
//   1. CORS — 오픈 API는 허용된 오리진의 브라우저 호출만 받는다
//   2. 보안 — API 키를 브라우저 코드에 넣으면 누구나 키를 볼 수 있다
// 따라서 위젯은 자기 서버(이 프록시)를 경유하고, 키는 서버 환경변수에만 둔다.
//
// 실행: node proxy.js  →  http://localhost:8787
//   YES24_API_KEY 미설정 시 sample-data.json 을 반환하는 "데모 모드"로 동작한다.

const http = require("http");
const https = require("https");
const fs = require("fs");
const path = require("path");

const PORT = Number(process.env.PORT || 8787);
const API_KEY = process.env.YES24_API_KEY || "";
const API_BASE = process.env.YES24_API_BASE_URL || "https://apis.yes24.com";
const DEMO_MODE = !API_KEY;

// 데모 모드용 가상 카테고리 목록 (실제 목록은 GET /v1/category/list 로 조회)
const DEMO_CATEGORIES = {
  success: true,
  message: "성공",
  data: {
    meta: { apiTitle: "카테고리 목록 조회 (데모)", version: "v1" },
    data: [
      { categoryId: "001", categoryName: "국내도서", categoryFullPath: "국내도서", categoryUrl: "" },
      { categoryId: "002", categoryName: "외국도서", categoryFullPath: "외국도서", categoryUrl: "" },
      { categoryId: "003", categoryName: "eBook", categoryFullPath: "eBook", categoryUrl: "" },
    ],
  },
  errorCode: null,
};

// 정적 파일 화이트리스트 — 경로 조작 방지를 위해 목록에 있는 파일만 서빙
const STATIC_FILES = {
  "/": { file: "index.html", type: "text/html; charset=utf-8" },
  "/index.html": { file: "index.html", type: "text/html; charset=utf-8" },
  "/sample-data.json": { file: "sample-data.json", type: "application/json; charset=utf-8" },
};

function sendJson(res, statusCode, body, extraHeaders = {}) {
  res.writeHead(statusCode, { "Content-Type": "application/json; charset=utf-8", ...extraHeaders });
  res.end(typeof body === "string" ? body : JSON.stringify(body));
}

// 오픈 API 로 요청을 전달하며 서버 측에서 X-Api-Key 를 주입한다
function forward(apiPath, res) {
  const target = new URL(apiPath, API_BASE);
  const mod = target.protocol === "http:" ? http : https;
  const upstream = mod.get(target, { headers: { "X-Api-Key": API_KEY } }, (up) => {
    res.writeHead(up.statusCode || 502, {
      "Content-Type": up.headers["content-type"] || "application/json; charset=utf-8",
    });
    up.pipe(res);
  });
  upstream.on("error", (err) => {
    sendJson(res, 502, { success: false, message: `오픈 API 호출 실패: ${err.message}`, data: null, errorCode: "PROXY_502" });
  });
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);

  // 베스트셀러 조회 — GET /api/bestseller?categoryId=001&pageSize=10
  if (url.pathname === "/api/bestseller") {
    if (DEMO_MODE) {
      res.setHeader("X-Demo-Mode", "1");
      const stream = fs.createReadStream(path.join(__dirname, "sample-data.json"));
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8", "X-Demo-Mode": "1" });
      stream.pipe(res);
      return;
    }
    const categoryId = url.searchParams.get("categoryId") || "001";
    const pageSize = url.searchParams.get("pageSize") || "10";
    forward(
      `/v1/category/bestseller?categoryId=${encodeURIComponent(categoryId)}&page=1&pageSize=${encodeURIComponent(pageSize)}`,
      res
    );
    return;
  }

  // 카테고리 목록 — GET /api/categories (위젯 셀렉트 박스 채우기용)
  if (url.pathname === "/api/categories") {
    if (DEMO_MODE) {
      sendJson(res, 200, DEMO_CATEGORIES, { "X-Demo-Mode": "1" });
      return;
    }
    forward("/v1/category/list", res);
    return;
  }

  // 정적 파일 (index.html, sample-data.json)
  const entry = STATIC_FILES[url.pathname];
  if (!entry) {
    sendJson(res, 404, { success: false, message: "Not Found", data: null, errorCode: "PROXY_404" });
    return;
  }
  res.writeHead(200, { "Content-Type": entry.type });
  fs.createReadStream(path.join(__dirname, entry.file)).pipe(res);
});

server.listen(PORT, () => {
  console.log(`예스24 베스트셀러 위젯: http://localhost:${PORT}`);
  console.log(DEMO_MODE
    ? "모드: 데모 (YES24_API_KEY 미설정 — sample-data.json 반환)"
    : `모드: 실서비스 (${API_BASE} 프록시)`);
});
