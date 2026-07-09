import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


@dataclass
class Article:
    id: str
    title: str
    source: str | None
    published: datetime | None
    url: str | None
    google_url: str
    full_text: str | None

    @property
    def date_published_string(self):
        return self.format_published("%B %d, %Y")
    
    # TODO make sure today on report is by hawaii time (maybe display on the UI)
    @property
    def time_published_string(self):
        if not self.published:
            return ""
        gmt_str = f"{self.format_published('%H:%M')} GMT"
        hst_datetime = self.published.astimezone(ZoneInfo("Pacific/Honolulu"))
        hst_str = f"{hst_datetime.strftime('%H:%M')} HST"
        full_str = f"{gmt_str} ({hst_str})"
        return full_str

    def format_published(self, format):
        if not self.published:
            return ""
        return self.published.strftime(format)

    @classmethod
    def from_rss_entry(cls, entry):
        id = cls.make_article_id(entry)
        title_source = entry.get("title", "")

        title, source = cls.separate_title_and_source(title_source)

        published = None
        published_parsed = entry.get("published_parsed")

        if published_parsed:
            published = datetime(*published_parsed[:6], tzinfo=timezone.utc)
        
        google_url = entry.link

        return Article(
            id=id, title=title, source=source, published=published, url=None, google_url=google_url, full_text=None
        )

    @staticmethod
    def make_article_id(entry) -> str:
        base = entry.get("id") or entry.get("guid") or entry.get("link") or entry.get("title")
        return hashlib.md5(base.encode()).hexdigest()

    @staticmethod
    def separate_title_and_source(title_source: str):
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