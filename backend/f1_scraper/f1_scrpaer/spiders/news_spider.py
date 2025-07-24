import scrapy
import spacy
from f1_scraper.items import F1NewsItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class NewsSpider(CrawlSpider):
    name = 'news_spider'
    
    # The curated list of top F1 news sources
    start_urls = [
        'https://www.formula1.com/en/latest',
        'https://www.motorsport.com/f1/news/',
        'https://www.autosport.com/f1/',
        'https://www.racefans.net/category/f1/',
        'https://the-race.com/formula-1/',
        'https://joesaward.wordpress.com/',
        'https://www.racingnews365.com/f1-news'
    ]

    # Rules to follow links. We only want to parse article pages.
    # This requires analyzing each site's URL structure.
    rules = (
        Rule(LinkExtractor(allow=r'\/news\/|\/article\/|\d{4}\/\d{2}\/\d{2}\/'), callback='parse_article', follow=True),
    )

    def __init__(self, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        # Load the spaCy model for NLP summarization
        self.nlp = spacy.load("en_core_web_sm")
        self.nlp.add_pipe("textrank")

    def start_requests(self):
        for url in self.start_urls:
            # Use Playwright for sites known to be dynamic/JS-heavy
            # A simple heuristic is used here; a more robust solution would
            # implement the escalating strategy from the blueprint.
            use_playwright = 'wordpress.com' not in url
            yield scrapy.Request(
                url,
                meta={'playwright': use_playwright}
            )

    def parse_article(self, response):
        """This function parses the individual article pages."""
        item = F1NewsItem()

        # --- Intelligent Image Extraction ---
        # Heuristic: Prioritize Open Graph/Twitter metadata tags for the main image
        og_image = response.xpath('//meta[@property="og:image"]/@content').get()
        twitter_image = response.xpath('//meta[@name="twitter:image"]/@content').get()
        
        image_url = og_image or twitter_image
        if not image_url:
            # Fallback: find the first prominent image in the main content area
            image_url = response.css('article img::attr(src)').get() or response.css('main img::attr(src)').get()

        # --- Content Extraction ---
        headline = response.css('h1::text').get('').strip()
        if not headline:
            headline = response.xpath('//meta[@property="og:title"]/@content').get('').strip()

        # Extract all text from the main article body for summarization
        # This selector is generic and would need to be refined for each site
        paragraphs = response.css('article p::text,.article-body p::text').getall()
        full_text = ' '.join(p.strip() for p in paragraphs if p.strip())

        if not headline or not full_text:
            # If we can't find a headline or text, it's probably not a valid article page
            return

        # --- NLP Text Summarization ---
        # Use spaCy with pytextrank for extractive summarization
        doc = self.nlp(full_text)
        # Get the top 2-3 sentences for the summary
        summary_sentences = [sent.text for sent in doc._.textrank.summary(limit_sentences=3)]
        summary = ' '.join(summary_sentences)

        # --- Load Data into Item ---
        item['headline'] = headline
        item['summary'] = summary if summary else full_text[:250] + '...' # Fallback summary
        item['image_url'] = response.urljoin(image_url) if image_url else None
        item['source_url'] = response.url
        item['full_text'] = full_text

        yield item