import os

# ─── Identitas Project ────────────────────────────────────────────────────────
BOT_NAME = "property_scraper"
SPIDER_MODULES = ["property_scraper.spiders"]
NEWSPIDER_MODULE = "property_scraper.spiders"

# ─── Anti-Bot: User-Agent Rotation ───────────────────────────────────────────
# scrapy-user-agents akan override ini secara otomatis jika diinstall
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# ─── Politeness ───────────────────────────────────────────────────────────────
ROBOTSTXT_OBEY = False          # Situs properti umumnya memblokir bot di robots.txt
DOWNLOAD_DELAY = 2              # Detik antar request (default, spider bisa override)
RANDOMIZE_DOWNLOAD_DELAY = True # Randomisasi ±50% dari DOWNLOAD_DELAY
CONCURRENT_REQUESTS = 4         # Maksimal request paralel keseluruhan
CONCURRENT_REQUESTS_PER_DOMAIN = 2  # Maks 2 request per domain secara bersamaan
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# ─── Cookies & Headers ────────────────────────────────────────────────────────
COOKIES_ENABLED = True
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
}

# ─── Middlewares ──────────────────────────────────────────────────────────────
DOWNLOADER_MIDDLEWARES = {
    # Playwright harus diaktifkan — menangani JS rendering
    "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler": None,  # handler, bukan middleware

    # Retry middleware (built-in)
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 550,

    # Custom middleware untuk logging & error handling
    "property_scraper.middlewares.LoggingMiddleware": 100,
}

# ─── Playwright ───────────────────────────────────────────────────────────────
DOWNLOAD_HANDLERS = {
    "http":  "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

PLAYWRIGHT_BROWSER_TYPE = "chromium"  # chromium | firefox | webkit
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "args": [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
    ],
}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30_000  # 30 detik
PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 4

# ─── Retry ────────────────────────────────────────────────────────────────────
RETRY_ENABLED = True
RETRY_TIMES = 2
RETRY_HTTP_CODES = [500, 502, 503, 504, 429, 403]

# ─── Item Pipelines ───────────────────────────────────────────────────────────
ITEM_PIPELINES = {
    "property_scraper.pipelines.ValidatePipeline": 100,   # Validasi field wajib
    "property_scraper.pipelines.DeduplicationPipeline": 200,  # Hapus duplikat
    "property_scraper.pipelines.JsonlExportPipeline": 300,  # Simpan ke JSONL
}

# ─── Output ───────────────────────────────────────────────────────────────────
FEEDS = {}  # Kosongkan — output dikelola oleh pipeline atau argumen -O di CLI

# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("SCRAPY_LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"

# ─── Misc ─────────────────────────────────────────────────────────────────────
TELNETCONSOLE_ENABLED = False
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"