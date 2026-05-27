import feedparser
import logging
import requests
import trafilatura

logger = logging.getLogger(__name__)

def get_news(query, num_articles):
    rss_url = "https://news.google.com/rss/search?q=" + query.replace(" ", "+")
    feed = feedparser.parse(rss_url)
    logger.info(f"Feed status: {feed.get('status')}")
    logger.debug(f"Feed: {feed}")
    logger.info(f"Found {len(feed.entries)} articles")

    articles = []

    for entry in feed.entries[:num_articles]:
        url = entry.link
        logger.info(f"Fetching news article:\n\t{entry.title}\n\tat url: {url}")

        try:
            response = requests.get(
                url,
                # user agent to look like a normal browser and avoid being blocked
                headers={
                    "User-Agent": "Mozilla/5.0"
                },
                timeout=15
            )
            response.raise_for_status()
            raw_text = response.text
            clean_text = trafilatura.extract(raw_text)
            articles.append({
                "title": entry.title,
                "url": url,
                "raw_text": raw_text,
                "clean_text": clean_text
            })
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news article: {e}")
            articles.append({
                "title": entry.title,
                "url": url,
                "error": str(e)
            })
            continue

    return articles