import feedparser
import logging
import requests
import trafilatura

from googlenewsdecoder import new_decoderv1


logger = logging.getLogger(__name__)


def decode_google_url(google_url):
    """Decode the encrypted redirect URL used by Google News into its original source URL"""
    logger.info(f"Attempting to decode Google redirect url: {google_url}")
    result = new_decoderv1(google_url)
    if result.get('status') and result.get('decoded_url'):
        return result['decoded_url']
    else:
        return ""

def get_news(query, num_articles):
    rss_url = "https://news.google.com/rss/search?q=" + query.replace(" ", "+")

    feed = feedparser.parse(rss_url)
    logger.info(f"Feed status: {feed.get('status')}")
    logger.debug(f"Feed: {feed}")
    logger.info(f"Found {len(feed.entries)} articles")

    articles = []

    for entry in feed.entries[:num_articles]:
        google_url = entry.link
        decoded_url = decode_google_url(google_url)
        if decoded_url == "":
            # For now, we just won't include these articles since we can't access the text anyway.
            # articles.append({
            #     "title": entry.title,
            #     "url": None,
            #     "text": None,
            # })
            continue

        logger.info(f"Fetching news article:\n\t{entry.title}\n\tat url: {decoded_url}")
        downloaded = trafilatura.fetch_url(decoded_url)
        clean_text = trafilatura.extract(downloaded)
        articles.append({
            "title": entry.title,
            "published_datetime": entry.published_parsed,
            "url": decoded_url,
            "text": clean_text
        })

    return articles