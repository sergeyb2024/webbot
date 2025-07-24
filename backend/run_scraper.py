# backend/run_scraper.py

import os
import sys
from pathlib import Path

# --- Add this block to fix the import path ---
# This finds the scraper's project directory and adds it to the path
# so Python knows where to look for the f1_scraper module.
project_root = Path(__file__).parent / 'f1_scraper'
sys.path.append(str(project_root))
# --- End of new block ---

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from f1_scraper.spiders.news_spider import NewsSpider

def main():
    """
    Runs the F1 news scraper.
    """
    print(f"[{__file__}] --- Running F1 News Scraper ---")

    # Set the settings module for the Scrapy project
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'f1_scraper.settings')

    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(NewsSpider)
    process.start()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")