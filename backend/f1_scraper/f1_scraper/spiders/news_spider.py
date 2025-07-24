import scrapy
import sqlite3
from datetime import datetime
import spacy
import pytextrank
from scrapy_playwright.page import PageMethod

class NewsSpider(scrapy.Spider):
    name = 'f1_news'

    custom_settings = {
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
            'timeout': 90 * 1000  # Increased to 90 seconds for safety
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'TWISTED_REACTOR': "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }

    def __init__(self, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        # Setup spaCy for summarization
        self.nlp = spacy.load("en_core_web_sm")
        if "textrank" not in self.nlp.pipe_names:
            self.nlp.add_pipe("textrank")

        # Setup database connection
        self.conn = sqlite3.connect('../f1_news.db')
        self.c = self.conn.cursor()
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS articles
            (title TEXT, url TEXT PRIMARY KEY, summary TEXT, published_date TEXT, image_url TEXT, full_text TEXT)
        ''')
        self.conn.commit()

    def start_requests(self):
        # The initial request that will be handled by Playwright
        yield scrapy.Request(
            url='https://www.motorsport.com/f1/news/',
            callback=self.parse,
            meta={'playwright': True, 'playwright_include_page': True},
            errback=self.errback,
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]

        # Try to accept the cookies, but don't fail if the button isn't there
        try:
            # Wait for the button to be visible, then click it.
            await page.wait_for_selector('#onetrust-accept-btn-handler', timeout=20000)
            await page.click('#onetrust-accept-btn-handler')
            self.log("SUCCESS: Cookie consent button clicked.")
        except Exception:
            self.log("INFO: Cookie consent button not found or timed out, proceeding anyway.")

        # Wait for the main content grid to be loaded
        try:
            await page.wait_for_selector('div.ms-grid-hor-items', timeout=20000)
            self.log("SUCCESS: Article grid found.")
        except Exception as e:
            self.log(f"ERROR: Could not find article grid. Page might have changed. Error: {e}")
            await page.close()
            return # Stop if we can't find the articles

        # Get the fully rendered HTML after all actions
        html_content = await page.content()
        await page.close()

        # Use Scrapy's Selector on the final HTML
        selector = scrapy.Selector(text=html_content)
        article_links = selector.css('a[data-type="post_item"]::attr(href)').getall()
        self.log(f"Found {len(article_links)} article links. Following them now.")

        for link in article_links:
            full_url = response.urljoin(link)
            # Use standard Scrapy requests for individual articles as they are simpler
            yield scrapy.Request(full_url, callback=self.parse_article)

    def parse_article(self, response):
        title = response.css('h1.ms-article-title::text').get()
        paragraphs = response.css('.ms-article-content p::text').getall()
        article_text = ' '.join(p.strip() for p in paragraphs if p.strip())
        image_url = response.css('div.ms-photo-main-container img::attr(src)').get()

        if title and article_text:
            doc = self.nlp(article_text)
            summary = ' '.join([sent.text for sent in doc._.textrank.summary(limit_phrases=4, limit_sents=4)])
            published_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                self.c.execute("INSERT OR IGNORE INTO articles (title, url, summary, published_date, image_url, full_text) VALUES (?, ?, ?, ?, ?, ?)",
                               (title.strip(), response.url, summary, published_date, image_url, article_text))
                self.conn.commit()
                self.log(f'SUCCESS: Saved article - {title.strip()}')
            except sqlite3.Error as e:
                self.log(f"DATABASE ERROR: {e}")

    async def errback(self, failure):
        self.log(f"ERROR: Playwright request failed: {repr(failure)}")
        if "playwright_page" in failure.request.meta:
            page = failure.request.meta["playwright_page"]
            await page.close()

    def close(self, reason):
        if self.conn:
            self.conn.close()
