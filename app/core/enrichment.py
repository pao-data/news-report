import logging

import streamlit as st
import trafilatura
from googlenewsdecoder import new_decoderv1

import utils.logging
from models.article import Article

# Note: I use streamlit for caching even though this makes the backend dependent on streamlit. I decided
# this was worth it since streamlit caching allows cache to persist between user sessions, and I don't envision
# this app ever being used with a different front-end.

logger = logging.getLogger(__name__)

@utils.logging.log_execution_time
def enrich_url(article: Article) -> Article:
    url = decode_google_url(article.google_url)

    return Article(
        **{**article.__dict__, "url": url}
    )

@utils.logging.log_execution_time
def enrich_full_text(article: Article) -> Article:
    url = article.url
    if not url:
        logging.warning("Cannot fetch full article text because no url for article.")
        return Article(**{**article.__dict__, "full_text": None})
    
    raw_html = fetch_raw_html(url, download_timeout=3)
    if not raw_html:
        logging.warning(f"Could not fetch any data from url: {url}")
        return Article(**{**article.__dict__, "full_text": None})

    full_text = extract_main_text(raw_html, favor_recall=True)
    if not full_text:
        logger.warning(f"Downloaded data could not be parsed by trafilatura for article at url {url}")
    
    return Article(
        **{**article.__dict__, "full_text": full_text}
    )

@st.cache_data
def decode_google_url(google_url: str, decoder=new_decoderv1) -> str | None:
    """Decode the encrypted redirect URL used by Google News into its original source URL"""
    logger.debug(f"Attempting to decode Google redirect url: {google_url}")
    result = decoder(google_url)
    if result.get('status') and result.get('decoded_url'):
        return result['decoded_url']
    else:
        return None
    
@st.cache_data
def fetch_raw_html(url: str, download_timeout: int):
    config = trafilatura.settings.use_config()
    config.set('DEFAULT', 'DOWNLOAD_TIMEOUT', str(download_timeout))
    return trafilatura.fetch_url(url, config=config)

@st.cache_data
def extract_main_text(raw_html, **kwargs):
    return trafilatura.extract(raw_html, **kwargs)