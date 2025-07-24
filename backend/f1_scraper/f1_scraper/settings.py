BOT_NAME = 'f1_scraper'

SPIDER_MODULES = ['f1_scraper.spiders']
NEWSPIDER_MODULE = 'f1_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# --- Playwright Settings for Dynamic Content ---
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "timeout": 20 * 1000,  # 20 seconds
}

# --- Anti-Scraping & Politeness Settings ---
# Set a realistic browser User-Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Configure AutoThrottle to be a polite scraper
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Configure a delay for requests for the same website
DOWNLOAD_DELAY = 3
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# --- Pipeline Configuration ---
ITEM_PIPELINES = {
   'f1_scraper.pipelines.F1NewsPipeline': 300,
}