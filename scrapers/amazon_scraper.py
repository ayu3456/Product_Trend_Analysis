import asyncio
from playwright.async_api import async_playwright
import logging
from typing import List, Dict, Any
import datetime

# Setup logging
logger = logging.getLogger(__name__)

class AmazonScraper:
    def __init__(self, max_reviews: int = 10):
        self.max_reviews = max_reviews
        self.base_url = "https://www.amazon.com/s?k="

    async def scrape(self, keyword: str) -> List[Dict[str, Any]]:
        """Scrapes Amazon for product reviews based on a keyword search."""
        results = []
        search_url = f"{self.base_url}{keyword}"
        
        logger.info(f"Scraping Amazon for keyword: {keyword}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            try:
                # Step 1: Find a product from search results
                await page.goto(search_url, wait_until="domcontentloaded")
                await page.wait_for_selector('.s-result-item', timeout=15000)
                
                # Get the first sponsored or non-sponsored product link
                product_link_el = await page.query_selector('h2 a.a-link-normal')
                if not product_link_el:
                    logger.warning("No products found on Amazon search page.")
                    return []
                
                product_url = await product_link_el.get_attribute('href')
                if not product_url.startswith('http'):
                    product_url = f"https://www.amazon.com{product_url}"
                
                # Step 2: Go to the "All Reviews" page for that product
                # We can modify the URL to go directly to reviews
                # Example: /product-reviews/ASIN/
                review_url = product_url.replace("/dp/", "/product-reviews/").split("?")[0]
                await page.goto(review_url, wait_until="domcontentloaded")
                
                # Step 3: Scrape individual reviews
                await page.wait_for_selector('.review', timeout=10000)
                reviews = await page.query_selector_all('.review')
                
                for review in reviews[:self.max_reviews]:
                    try:
                        title_el = await review.query_selector('.review-title-content')
                        title = await title_el.inner_text() if title_el else ""
                        
                        body_el = await review.query_selector('.review-text-content')
                        body = await body_el.inner_text() if body_el else ""
                        
                        full_text = f"{title}. {body}".strip()
                        
                        date_el = await review.query_selector('.review-date')
                        date_text = await date_el.inner_text() if date_el else ""
                        
                        results.append({
                            "platform": "Amazon",
                            "keyword": keyword,
                            "text": full_text,
                            "url": review_url,
                            "timestamp": date_text or datetime.datetime.now().isoformat()
                        })
                    except Exception as e:
                        logger.warning(f"Failed to parse an Amazon review: {e}")
                        continue
                
                logger.info(f"Successfully scraped {len(results)} reviews from Amazon.")
                
            except Exception as e:
                logger.error(f"Error during Amazon scraping: {e}")
            finally:
                await browser.close()
                
        return results

if __name__ == "__main__":
    scraper = AmazonScraper(max_reviews=5)
    data = asyncio.run(scraper.scrape("MacBook Pro"))
    for d in data:
        print(f"--- {d['platform']} ---\n{d['text'][:100]}...")
