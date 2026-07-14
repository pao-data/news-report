import logging
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import feedparser
import requests
from models.article import Article

logger = logging.getLogger(__name__)


def create_search_url(user_query: str):
    normalized = re.sub(r"\s+", " ", user_query).strip()

    rss_url = f"https://news.google.com/rss/search?q={quote(normalized)}+when:1d"
    logger.info(f"RSS url:\t{rss_url}")
    return rss_url


def get_articles_from_rss(query: str, limit: int | None = None) -> list[Article]:
    """Get articles from Google RSS for the given search query within the past 24 hours."""
    rss_url = create_search_url(query)
    response = requests.get(rss_url, timeout=10)
    response.raise_for_status()
    feed = feedparser.parse(response.content)

    logger.info(f"Feed status: {feed.get('status')}")
    logger.debug(f"Feed: {feed}")
    logger.info(f"Found {len(feed.entries)} articles")

    cutoff = datetime.now(timezone.utc) - timedelta(days=1)
    filtered_entries = []
    for entry in feed.entries:
        published = Article.parse_published_parsed(getattr(entry, "published_parsed", None))
        if published and published >= cutoff:
            filtered_entries.append(entry)
    articles = [Article.from_rss_entry(entry) for entry in filtered_entries]

    if limit:
        articles = articles[:limit]

    return articles
