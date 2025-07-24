import scrapy

class F1NewsItem(scrapy.Item):
    headline = scrapy.Field()
    summary = scrapy.Field()
    image_url = scrapy.Field()
    source_url = scrapy.Field()
    full_text = scrapy.Field() # For better searchability