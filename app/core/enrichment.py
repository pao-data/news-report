import logging

import trafilatura
from googlenewsdecoder import new_decoderv1

from models.article import Article

logger = logging.getLogger(__name__)


def enrich_url(article: Article) -> Article:
    url = decode_google_url(article.google_url)

    return Article(
        **{**article.__dict__, "url": url}
    )

def enrich_full_text(article: Article) -> Article:
    url = article.url
    if not url:
        logging.warning("Cannot fetch full article text because no url for article.")
        return Article(**{**article.__dict__, "full_text": None})

    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        logging.warning(f"Could not fetch any data from url: {url}")
        return Article(**{**article.__dict__, "full_text": None})
    
    full_text = trafilatura.extract(downloaded)
    if not full_text:
        logger.warning(f"Downloaded data could not be parsed by trafilatura for article at url {url}")
    
    return Article(
        **{**article.__dict__, "full_text": full_text}
    )

def decode_google_url(google_url: str, decoder=new_decoderv1) -> str | None:
    """Decode the encrypted redirect URL used by Google News into its original source URL"""
    logger.info(f"Attempting to decode Google redirect url: {google_url}")
    result = decoder(google_url)
    if result.get('status') and result.get('decoded_url'):
        return result['decoded_url']
    else:
        return None
    
