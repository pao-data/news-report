import hashlib
import logging
import requests
import time
import os
import random
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Self
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
from newsplease import NewsPlease
from googlenewsdecoder import new_decoderv1

logger = logging.getLogger(__name__)


@dataclass
class Article:
    """Canonical article model used throughout search/layout/report flows."""

    id: str
    title: str
    source: str | None
    #author: str | None
    published: datetime | None
    url: str | None
    google_url: str
    full_text: str | None

    @property
    def date_published_string(self) -> str:
        return self.format_published("%B %d, %Y")

    # TODO make sure today on report is by hawaii time (maybe display on the UI)
    @property
    def time_published_string(self) -> str:
        if not self.published:
            return ""
        gmt_str = f"{self.format_published('%H:%M')} GMT"
        hst_datetime = self.published.astimezone(ZoneInfo("Pacific/Honolulu"))
        hst_str = f"{hst_datetime.strftime('%H:%M')} HST"
        full_str = f"{gmt_str} ({hst_str})"
        return full_str

    def format_published(self, format: str) -> str:
        if not self.published:
            return ""
        return self.published.strftime(format)

    @classmethod
    def from_rss_entry(cls, entry: Any) -> Self:
        id = cls.make_article_id(entry)
        title_source = entry.get("title", "")

        title, source = cls.separate_title_and_source(title_source)

        published = cls.parse_published_parsed(entry.get("published_parsed"))

        google_url = entry.link
        #try:
        #'''
        #decoder=new_decoderv1
        #decoded_url = ""
        #result = decoder(google_url)
        #if result.get("status") and result.get("decoded_url"):
        #    decoded_url = result["decoded_url"]
        #else:
        #    RuntimeError(result["message"])
        #'''
        #decoded_url = decoder(google_url)
        #except RuntimeError as e:
        #    logger.warning(f"url decoding failed: {e}")
        #    decoded_url = None
        #url = decode_google_url(google_url)
        #author = entry.get("author", "")
        #url = "https://www.aerotime.aero/articles/australia-us-japan-formalize-new-trilateral-air-logistics-agreement"
        #---
        #time.sleep(10)
        #response = requests.get(google_url)
        #soup = BeautifulSoup(response.text, "html.parser")
        #author_tag = soup.find("meta", attrs={"name": "author"})
        #if author_tag:
        #    author = str(author_tag.get("content"))
        #else:
        #    author = entry.get("author", "")
        #---
        return cls(
            id=id,
            title=title,
            source=source,
            #author=None,
            published=published,
            url=None,
            google_url=google_url,
            full_text=None,
        )

    @staticmethod
    def make_article_id(entry: Any) -> str:
        base = entry.get("id") or entry.get("guid") or entry.get("link") or entry.get("title")
        return hashlib.md5(base.encode()).hexdigest()

    @staticmethod
    def parse_published_parsed(published_parsed: Any) -> datetime | None:
        if not isinstance(published_parsed, Sequence) or len(published_parsed) < 6:
            return None
        try:
            parts = tuple(int(part) for part in published_parsed[:6])
            return datetime(*parts, tzinfo=timezone.utc)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def separate_title_and_source(title_source: str) -> tuple[str, str]:
        parts = title_source.split(" - ")

        if len(parts) != 2:
            logger.warning(
                "Expected 2 parts when splitting the title element from the rss feed into title and source,"
                f"got {len(parts)}: {title_source}",
            )

        if len(parts) == 1:
            title = parts[0]
            source = ""
        elif len(parts) == 2:
            title, source = parts
        else:
            # Making the assumption that the extra " - " would be in the title rather than the source.
            source = parts[-1]
            title = " - ".join(parts[:-1])

        return title, source

#    def checkForAuthor():
#        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
#        meta = soup.find('meta', {'name': 'byl'})
#        return meta is not None
