import sqlite3

class F1NewsPipeline:
    def open_spider(self, spider):
        # Get the database path from the settings passed by run_scraper.py
        db_path = spider.settings.get('DATABASE_PATH', 'f1_news.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        """Create the articles table if it doesn't exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                headline TEXT NOT NULL,
                summary TEXT,
                image_url TEXT,
                source_url TEXT UNIQUE,
                full_text TEXT
            )
        ''')
        self.conn.commit()

    def process_item(self, item, spider):
        """
        Save the scraped item to the database.
        The 'UNIQUE' constraint on source_url prevents duplicate entries.
        """
        try:
            self.cursor.execute(
                'INSERT OR IGNORE INTO articles (headline, summary, image_url, source_url, full_text) VALUES (?,?,?,?,?)',
                (
                    item.get('headline'),
                    item.get('summary'),
                    item.get('image_url'),
                    item.get('source_url'),
                    item.get('full_text')
                )
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            spider.logger.warning(f"Duplicate item found: {item['source_url']}")
        return item

    def close_spider(self, spider):
        self.conn.close()