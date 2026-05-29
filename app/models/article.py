from dataclasses import dataclass
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class Article:
    id: str
    title: str
    source: str | None
    published: datetime
    url: str | None
    google_url: str
    full_text: str | None

    @property
    def date_published_string(self, format="%B %d, %Y"):
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
            published = datetime(*published_parsed[:6])
        
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