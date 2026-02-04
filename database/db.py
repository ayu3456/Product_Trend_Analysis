import sqlite3
import logging
from typing import List, Dict, Any, Optional
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "sentiment_dashboard.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initializes the database schema."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Table for raw data from scrapers
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS raw_posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        platform TEXT NOT NULL,
                        keyword TEXT NOT NULL,
                        raw_text TEXT NOT NULL,
                        source_url TEXT,
                        post_timestamp TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Table for processed/cleaned text
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS processed_posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        raw_post_id INTEGER,
                        cleaned_text TEXT NOT NULL,
                        FOREIGN KEY (raw_post_id) REFERENCES raw_posts(id)
                    )
                """)
                
                # Table for sentiment analysis results
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sentiment_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        processed_post_id INTEGER,
                        sentiment_label TEXT NOT NULL,
                        confidence_score REAL NOT NULL,
                        model_name TEXT NOT NULL,
                        FOREIGN KEY (processed_post_id) REFERENCES processed_posts(id)
                    )
                """)
                
                conn.commit()
                logger.info("Database initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")

    def insert_raw_post(self, data: Dict[str, Any]) -> int:
        """Inserts a raw post and returns its ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO raw_posts (platform, keyword, raw_text, source_url, post_timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (data['platform'], data['keyword'], data['text'], data.get('url'), data.get('timestamp')))
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error inserting raw post: {e}")
            return -1

    def insert_processed_post(self, raw_post_id: int, cleaned_text: str) -> int:
        """Inserts a processed post and returns its ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO processed_posts (raw_post_id, cleaned_text)
                    VALUES (?, ?)
                """, (raw_post_id, cleaned_text))
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error inserting processed post: {e}")
            return -1

    def insert_sentiment_result(self, processed_post_id: int, label: str, score: float, model: str):
        """Inserts sentiment analysis results."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sentiment_results (processed_post_id, sentiment_label, confidence_score, model_name)
                    VALUES (?, ?, ?, ?)
                """, (processed_post_id, label, score, model))
        except sqlite3.Error as e:
            logger.error(f"Error inserting sentiment result: {e}")

    def get_dashboard_data(self, keyword: str, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetches joined data for the dashboard visualization."""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = """
                    SELECT 
                        rp.platform, 
                        rp.raw_text, 
                        pp.cleaned_text, 
                        sr.sentiment_label, 
                        sr.confidence_score, 
                        rp.post_timestamp,
                        sr.model_name
                    FROM raw_posts rp
                    JOIN processed_posts pp ON rp.id = pp.raw_post_id
                    JOIN sentiment_results sr ON pp.id = sr.processed_post_id
                    WHERE rp.keyword = ?
                """
                params = [keyword]
                
                if platform:
                    query += " AND rp.platform = ?"
                    params.append(platform)
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching dashboard data: {e}")
            return []

if __name__ == "__main__":
    db = DatabaseManager()
    print("Database manager ready.")
