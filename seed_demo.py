from database.db import DatabaseManager
from preprocessing.clean_text import TextPreprocessor
from models.sentiment_model import SentimentAnalyzer
import datetime
import random

import yaml

def load_config():
    with open("config.yaml", 'r') as f:
        return yaml.safe_load(f)

def seed_data(keyword="iPhone"):
    config = load_config()
    db = DatabaseManager(config['database']['db_path'])
    preprocessor = TextPreprocessor()
    analyzer = SentimentAnalyzer("BERT") # Use BERT for speed
    
    platforms = ["Reddit", "Amazon", "Twitter"]
    samples = [
        # Reddit
        {"platform": "Reddit", "text": "I just got the new iPhone and the battery life is insane! Best purchase ever.", "url": "https://reddit.com/r/iphone/1"},
        {"platform": "Reddit", "text": "The new update is buggy. My phone keeps crashing every 10 minutes. So frustrating.", "url": "https://reddit.com/r/iphone/2"},
        {"platform": "Reddit", "text": "Is it worth upgrading from 13 to 15? The camera looks good but the price is high.", "url": "https://reddit.com/r/iphone/3"},
        # Amazon
        {"platform": "Amazon", "text": "5 stars. Amazing screen and very fast. Highly recommend to anyone.", "url": "https://amazon.com/dp/B01"},
        {"platform": "Amazon", "text": "Disappointed. The package arrived damaged and the phone screen was cracked.", "url": "https://amazon.com/dp/B02"},
        {"platform": "Amazon", "text": "It's a phone. It works. Nothing special for the high price tag.", "url": "https://amazon.com/dp/B03"},
        # Twitter
        {"platform": "Twitter", "text": "Just saw the new iPhone colors. The blue one is stunning! #Apple #iPhone", "url": "https://twitter.com/user/status/1"},
        {"platform": "Twitter", "text": "Why is the charger still sold separately? Greedy move by Apple. #iPhone #fail", "url": "https://twitter.com/user/status/2"},
        {"platform": "Twitter", "text": "Switching from Android to iPhone today. Wish me luck! #NewPhone", "url": "https://twitter.com/user/status/3"},
    ]
    
    # Generate some historical data for the line chart
    today = datetime.datetime.now()
    
    print(f"Seeding demo data for: {keyword}")
    for i, item in enumerate(samples):
        # Add a random timestamp from the last 5 days
        days_ago = random.randint(0, 5)
        timestamp = (today - datetime.timedelta(days=days_ago)).isoformat()
        
        item['keyword'] = keyword
        item['timestamp'] = timestamp
        
        # Process and Predict
        cleaned = preprocessor.clean(item['text'])
        sentiment = analyzer.predict(cleaned)
        
        # Store
        raw_id = db.insert_raw_post(item)
        proc_id = db.insert_processed_post(raw_id, cleaned)
        db.insert_sentiment_result(proc_id, sentiment['label'], sentiment['score'], "BERT")
        
    print("Seeding complete. Restart the dashboard to see result.")

if __name__ == "__main__":
    seed_data("iPhone")
