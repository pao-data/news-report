import hashlib
import json
import logging
import trafilatura
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Self
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


@dataclass
class Article:
    """Canonical article model used throughout search/layout/report flows."""

    id: str | None
    title: str | None
    source: str | None
    author: str | None
    published: datetime | None
    url: str | None
    google_url: str | None
    full_text: str | None
    is_manual_entry: bool

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

        return cls(
            id=id,
            title=title,
            source=source,
            author=None,
            published=published,
            url=None,
            google_url=google_url,
            full_text=None,
            is_manual_entry=False
        )

    @classmethod
    def from_manual_entry(cls, entry: Any) -> Self:
        id = cls.make_article_id(entry)
        title = None
        source = None
        author = None
        published = None
        # url = entry
        google_url = None
        full_text = None

        raw_html = trafilatura.fetch_url(entry)
        if not raw_html:
            logging.warning(f"Could not fetch any data from url: {entry}")

        metadata = trafilatura.extract(raw_html, output_format="json", with_metadata=True)

        if metadata:
            metadata_json = json.loads(metadata)
            title = metadata_json['title']
            source = metadata_json['source-hostname']
            author = metadata_json['author']
            published = datetime.strptime(metadata_json['date'],'%Y-%m-%d')
            full_text = metadata_json['raw_text']

        return cls(
            id = id,
            title = title,
            source = source,
            author = author,
            published = published,
            url = entry,
            google_url = google_url,
            full_text = full_text,
            is_manual_entry = True
        )
        
    @staticmethod
    def make_article_id(entry: Any) -> str:
        try:
            base = entry.get("id") or entry.get("guid") or entry.get("link") or entry.get("title")
            encoded_id = hashlib.md5(base.encode()).hexdigest()
        except:
            # if article is inputted manually, then url will be used to generate id
            encoded_id = hashlib.md5(entry.encode()).hexdigest()
        return encoded_id

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