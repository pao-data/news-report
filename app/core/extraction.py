import logging

import streamlit as st
import trafilatura
import utils.logging
from googlenewsdecoder import new_decoderv1
from models.article import Article

# Note: I use streamlit for caching even though this makes the backend dependent on streamlit. I decided
# this was worth it since streamlit caching allows cache to persist between user sessions, and I don't envision
# this app ever being used with a different front-end.

logger = logging.getLogger(__name__)


@utils.logging.log_execution_time
def enrich_url(article: Article) -> Article:
    try:
        url = decode_google_url(article.google_url)
    except RuntimeError as e:
        logger.warning(f"url decoding failed: {e}")
        url = None

    return Article(**{**article.__dict__, "url": url})


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

    full_text = extract_main_text(raw_html, favor_recall=False)
    if not full_text:
        logger.warning(
            f"Downloaded data could not be parsed by trafilatura for article at url {url}"
        )

    return Article(**{**article.__dict__, "full_text": full_text})


@st.cache_data(show_spinner=False)
def decode_google_url(google_url: str, decoder=new_decoderv1) -> str | None:
    """Decode the encrypted redirect URL used by Google News into its original source URL"""
    logger.debug(f"Attempting to decode Google redirect url: {google_url}")
    result = decoder(google_url)
    if result.get("status") and result.get("decoded_url"):
        return result["decoded_url"]
    else:
        RuntimeError(result["message"])


@st.cache_data(show_spinner=False)
def fetch_raw_html(url: str, download_timeout: int):
    config = trafilatura.settings.use_config()
    config.set("DEFAULT", "DOWNLOAD_TIMEOUT", str(download_timeout))
    return trafilatura.fetch_url(url, config=config)


@st.cache_data(show_spinner=False)
def extract_main_text(raw_html, **kwargs):
    return trafilatura.extract(raw_html, **kwargs)


if __name__ == "__main__":
    gurl = "https://news.google.com/rss/articles/CBMi8AFBVV95cUxPaDI4U1hnSllxdjQwVk5MSmZRczl1VTdGODhrWlN2X3BFdTVJa3h2QWFqZmdTWk1SV2J4ajYzaGVvQUUwSmszbnByQW02eFNDUFNpMjN2MkI5Z3hqV29ZQUxaSWpxVGQwdy1UcE5feEQ4WWhoV1NMclYzb2FmOWNUZzhZX3JIOUtnWi10Ymh2M0w2S3d2M0Q0MjR3TkdLYS1GWHVpcmNjV2ItUHFqdzVERWVrakNPOGt6QkFhck1wN3J1YjVxSURrbHlHY3Y1Ym8xbERpM3pCZ3JSSkhMNnlJOXR6RmFEVVdobTJKdmI0WWHSAfYBQVVfeXFMUGZaTkNZRldPbDZoRXVUcC1KLW53RjZ6MEJraDN4dVVBaWpfam5Bcm92V2VkcHRQM3J4Qmprb0ZlLWJwN2NwRUF3LVl4REdqZEU1VUd1UWVubWFKMkgtX3FhbUpzR1JiamxJMjFfQXFlVWp2MUVpSUdpUXlNd3R2NEpwMUVVUE1BTjBFTE1HbThndDZBWHl4SXNfeTJqcnE5Z3hQeFRWaUJBUEVnZ1pBeDdZbTlGREZMbHQyM0U4UEVQa2xBYWpJaDNtSWlRMjlaMGtIZU5xTldBTl9EZExrNHVraEU1MFRmb1ZNVjBPOG43dXRWM3ln?oc=5"
    durl = decode_google_url(gurl)
    print(durl)
    print(new_decoderv1(gurl))
