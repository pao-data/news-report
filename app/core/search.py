import feedparser
import logging
import re
from urllib.parse import quote

from models.article import Article

logger = logging.getLogger(__name__)

def create_search_url(user_query: str):
    normalized = re.sub(r"\s+", " ", user_query).strip()

    google_query = f"{normalized} when:1d"

    rss_url = (
        "https://news.google.com/rss/search?"
        f"q={quote(google_query)}"
    )
    return rss_url

def get_articles_from_rss(query: str, limit: int | None = None) -> Article:
    """Get articles from Google RSS for the given search query within the past 24 hours."""
    rss_url = create_search_url(query)
    feed = feedparser.parse(rss_url)

    logger.info(f"Feed status: {feed.get('status')}")
    logger.debug(f"Feed: {feed}")
    logger.info(f"Found {len(feed.entries)} articles")

    articles = [Article.from_rss_entry(entry) for entry in feed.entries]

    if limit:
        articles = articles[:limit]
        
    return articles