import asyncio
from playwright.async_api import async_playwright
import logging
from typing import List, Dict, Any
import datetime

# Setup logging
logger = logging.getLogger(__name__)

class RedditScraper:
    def __init__(self, max_posts: int = 20):
        self.max_posts = max_posts
        self.base_url = "https://www.reddit.com/search/?q="

    async def scrape(self, keyword: str) -> List[Dict[str, Any]]:
        """Scrapes Reddit for a given keyword using Playwright."""
        results = []
        search_url = f"{self.base_url}{keyword}&sort=relevance"
        
        logger.info(f"Scraping Reddit for: {keyword}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-blink-features=AutomationControlled']
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                viewport={'width': 1280, 'height': 720}
            )
            page = await context.new_page()
            
            try:
                await page.goto(search_url, wait_until="networkidle")
                
                # Wait for results to load
                await page.wait_for_selector('shreddit-post', timeout=10000)
                
                # Scroll a bit to load more content if needed
                for _ in range(3):
                    await page.mouse.wheel(0, 2000)
                    await asyncio.sleep(1)

                # Collect post data
                posts = await page.query_selector_all('shreddit-post')
                
                for post in posts[:self.max_posts]:
                    try:
                        # Extract title and content
                        title = await post.get_attribute('post-title')
                        content_element = await post.query_selector('div[slot="text-body"]')
                        content = await content_element.inner_text() if content_element else ""
                        
                        full_text = f"{title}. {content}"
                        
                        # Extract other info
                        url_element = await post.query_selector('a[slot="full-post-link"]')
                        url = await url_element.get_attribute('href') if url_element else ""
                        if url and not url.startswith('http'):
                            url = f"https://www.reddit.com{url}"
                            
                        timestamp = await post.get_attribute('created-timestamp')
                        
                        results.append({
                            "platform": "Reddit",
                            "keyword": keyword,
                            "text": full_text,
                            "url": url,
                            "timestamp": timestamp or datetime.datetime.now().isoformat()
                        })
                    except Exception as e:
                        logger.warning(f"Failed to parse a Reddit post: {e}")
                        continue
                        
                logger.info(f"Successfully scraped {len(results)} posts from Reddit.")
                
            except Exception as e:
                logger.error(f"Error during Reddit scraping: {e}")
            finally:
                await browser.close()
                
        return results

if __name__ == "__main__":
    scraper = RedditScraper(max_posts=5)
    data = asyncio.run(scraper.scrape("OpenAI"))
    for d in data:
        print(f"--- {d['platform']} ---\n{d['text'][:100]}...")
