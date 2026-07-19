using System.Net;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;

// 예스24 오픈 API 도서 검색 샘플 (.NET 10, 외부 패키지 없음)
// 실행: dotnet run -- "클린 코드" [카테고리]

Console.OutputEncoding = Encoding.UTF8;

if (args.Length == 0)
{
    Console.WriteLine("사용법: dotnet run -- \"검색어\" [카테고리]");
    Console.WriteLine("  카테고리: ALL(기본), BOOK(국내도서), FOREIGN(외국도서), EBOOK, MUSIC, DVD");
    Console.WriteLine("  예시:    dotnet run -- \"클린 코드\" BOOK");
    return 1;
}

var apiKey = Environment.GetEnvironmentVariable("YES24_API_KEY");
if (string.IsNullOrWhiteSpace(apiKey))
{
    Console.WriteLine("환경변수 YES24_API_KEY 가 설정되지 않았습니다.");
    Console.WriteLine("예스24 개발자센터(https://developers.yes24.com)에서 API 키를 발급받아 설정하세요.");
    Console.WriteLine("  PowerShell : $env:YES24_API_KEY = \"발급받은키\"");
    Console.WriteLine("  cmd        : set YES24_API_KEY=발급받은키");
    Console.WriteLine("  bash/zsh   : export YES24_API_KEY=발급받은키");
    return 1;
}

var baseUrl  = Environment.GetEnvironmentVariable("YES24_API_BASE_URL") ?? "https://apis.yes24.com";
var query    = args[0];
var category = args.Length > 1 ? args[1].ToUpperInvariant() : "ALL";

using var http = new HttpClient { BaseAddress = new Uri(baseUrl) };
http.DefaultRequestHeaders.Add("X-Api-Key", apiKey);

var url = $"/v1/goods/itemList?query={Uri.EscapeDataString(query)}&category={category}&page=1&pageSize=10";
using var response = await http.GetAsync(url);

// 요청 한도 초과(5회/초, 5,000회/일) 시 429와 Retry-After 헤더가 반환된다
if (response.StatusCode == HttpStatusCode.TooManyRequests)
{
    var retryAfter = response.Headers.RetryAfter?.Delta?.TotalSeconds ?? 1;
    Console.WriteLine($"요청 한도를 초과했습니다(429). {retryAfter}초 후 다시 시도하세요.");
    return 1;
}

ApiResponse<PageData<Book>>? result;
try
{
    result = await response.Content.ReadFromJsonAsync<ApiResponse<PageData<Book>>>(JsonSerializerOptions.Web);
}
catch (JsonException)
{
    Console.WriteLine($"응답을 해석할 수 없습니다. HTTP {(int)response.StatusCode}");
    return 1;
}

if (result is null || !result.Success || result.Data is null)
{
    Console.WriteLine($"오류: [{result?.ErrorCode ?? ((int)response.StatusCode).ToString()}] {result?.Message ?? "요청에 실패했습니다."}");
    return 1;
}

Console.WriteLine();
Console.WriteLine($"\"{query}\" 검색 결과 총 {result.Data.TotalCount:N0}건 중 상위 {result.Data.Items.Count}건");
Console.WriteLine(new string('─', 60));

var no = 1;
foreach (var book in result.Data.Items)
{
    Console.WriteLine($"{no,2}. {book.Title}");
    Console.WriteLine($"    {book.Author} | {book.Publisher} | {book.PublishDate}");
    Console.WriteLine($"    정가 {book.ShopPrice:N0}원 → 판매가 {book.SalePrice:N0}원 | ISBN13 {book.Isbn13}");
    Console.WriteLine($"    {book.Link}");
    Console.WriteLine();
    no++;
}
return 0;

// ── 응답 매핑용 최소 DTO (camelCase 는 JsonSerializerOptions.Web 이 자동 매핑) ──
internal record ApiResponse<T>(bool Success, string? Message, T? Data, string? ErrorCode);

internal record PageData<T>(List<T> Items, int CurrentPage, int PageSize, int TotalCount);

internal record Book(
    long ItemId,
    string? Title,
    string? Author,
    string? Publisher,
    string? Isbn13,
    decimal ShopPrice,
    decimal SalePrice,
    string? PublishDate,
    string? Cover,
    string? Link);
