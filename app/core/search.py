import feedparser
import logging

from models.article import Article

logger = logging.getLogger(__name__)


def get_articles_from_rss(query: str, limit: int | None = None) -> Article:
    """Get articles from Google RSS for the given search query within the past 24 hours."""
    rss_url = "https://news.google.com/rss/search?q=" + query.replace(" ", "%20") + "%20when:1d"
    feed = feedparser.parse(rss_url)

    logger.info(f"Feed status: {feed.get('status')}")
    logger.debug(f"Feed: {feed}")
    logger.info(f"Found {len(feed.entries)} articles")

    articles = [Article.from_rss_entry(entry) for entry in feed.entries]

    if limit:
        articles = articles[:limit]
        
    return articles