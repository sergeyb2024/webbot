import time
import os
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

# --- Path Setup ---
# Get the absolute path to the directory of this script (the 'backend' folder)
backend_dir = os.path.dirname(os.path.abspath(__file__))
# Add the backend directory to the Python path.
# This allows Python to find the 'f1_scraper' project module.
sys.path.insert(0, backend_dir)
# --- End Path Setup ---

def run_scraper_periodically(interval_seconds=900):
    """
    This function runs the Scrapy spider programmatically, waits for a
    specified interval, and then repeats.
    """
    # **THIS IS THE CORRECTED LINE**
    # It correctly sets a key in the os.environ dictionary.
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'f1_scraper.f1_scraper.settings'
    
    # Get Scrapy project settings. It will use the environment variable we just set.
    settings = get_project_settings()
    
    # Construct the absolute path to the database file and add it to the settings
    db_path = os.path.join(backend_dir, 'f1_news.db')
    settings.set('DATABASE_PATH', db_path)

    while True:
        print(f"[{time.ctime()}] --- Running F1 News Scraper ---")
        try:
            # Configure logging to see Scrapy's output in the console
            configure_logging()
            
            # Create a CrawlerProcess with the updated settings
            process = CrawlerProcess(settings)
            
            # The spider name is 'news_spider'
            process.crawl('news_spider')
            
            # The script will block here until the crawling is finished
            process.start()
            
            print(f"[{time.ctime()}] --- Scraper finished. Waiting for {interval_seconds / 60} minutes. ---")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        time.sleep(interval_seconds)

if __name__ == "__main__":
    # Run every 15 minutes (900 seconds)
    run_scraper_periodically(900)