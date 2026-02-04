import asyncio
from playwright.async_api import async_playwright
import logging
from typing import List, Dict, Any
import datetime

# Setup logging
logger = logging.getLogger(__name__)

class TwitterScraper:
    def __init__(self, max_tweets: int = 10):
        self.max_tweets = max_tweets
        # Using a public search mirror or nitter if possible, but for this demo 
        # we'll target x.com and handle the login wall gracefully.
        self.base_url = "https://twitter.com/search?q="

    async def scrape(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Scrapes Twitter (X) for a given keyword.
        Note: Twitter often requires login for search. This is a best-effort implementation.
        """
        results = []
        search_url = f"{self.base_url}{keyword}&src=typed_query&f=live"
        
        logger.info(f"Scraping Twitter for: {keyword}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                await page.goto(search_url, wait_until="networkidle")
                
                # Check for login wall
                if "login" in page.url:
                    logger.warning("Twitter redirected to login page. Scraping without auth is highly restricted.")
                    # In a real scenario, you'd provide session cookies or credentials.
                    # For this project, we return an empty list or a message.
                    return []

                # Wait for tweets to load
                await page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)
                
                tweets = await page.query_selector_all('article[data-testid="tweet"]')
                
                for tweet in tweets[:self.max_tweets]:
                    try:
                        # Extract tweet text
                        text_el = await tweet.query_selector('div[data-testid="tweetText"]')
                        text = await text_el.inner_text() if text_el else ""
                        
                        # Extract timestamp
                        time_el = await tweet.query_selector('time')
                        timestamp = await time_el.get_attribute('datetime') if time_el else ""
                        
                        # Extract post URL
                        link_el = await tweet.query_selector('a[href*="/status/"]')
                        tweet_url = await link_el.get_attribute('href') if link_el else ""
                        if tweet_url and not tweet_url.startswith('http'):
                            tweet_url = f"https://twitter.com{tweet_url}"
                            
                        results.append({
                            "platform": "Twitter",
                            "keyword": keyword,
                            "text": text,
                            "url": tweet_url,
                            "timestamp": timestamp or datetime.datetime.now().isoformat()
                        })
                    except Exception as e:
                        logger.warning(f"Failed to parse a tweet: {e}")
                        continue
                        
                logger.info(f"Successfully scraped {len(results)} tweets from Twitter.")
                
            except Exception as e:
                logger.error(f"Error during Twitter scraping: {e}")
            finally:
                await browser.close()
                
        return results

if __name__ == "__main__":
    scraper = TwitterScraper(max_tweets=5)
    data = asyncio.run(scraper.scrape("Tesla"))
    for d in data:
        print(f"--- {d['platform']} ---\n{d['text'][:100]}...")
