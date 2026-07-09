import sys
import types
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import cast
from unittest.mock import patch

from path_setup import ensure_app_on_path

# Keep tests runnable even when optional app deps are not installed.
if "feedparser" not in sys.modules:
    feedparser_stub = types.ModuleType("feedparser")
    setattr(feedparser_stub, "parse", lambda *_args, **_kwargs: None)
    sys.modules["feedparser"] = feedparser_stub

ensure_app_on_path()
from core.search import create_search_url, get_articles_from_rss


def make_entry(title: str, link: str, dt: datetime, entry_id: str):
    parsed = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, 0, 0, 0)
    return SimpleNamespace(
        link=link,
        published_parsed=parsed,
        get=lambda key, default=None: {
            "title": title,
            "published_parsed": parsed,
            "id": entry_id,
        }.get(key, default),
    )


class TestSearch(unittest.TestCase):
    def test_create_search_url_normalizes_whitespace(self):
        url = create_search_url("  drones    in    pacific   ")
        self.assertIn("drones%20in%20pacific", url)
        self.assertTrue(url.endswith("+when:1d"))

    @patch("core.search.feedparser.parse")
    def test_get_articles_from_rss_filters_to_last_24_hours(self, parse_mock):
        now = datetime.now(timezone.utc)
        recent_entry = make_entry("Recent - Source", "https://example.com/recent", now - timedelta(hours=2), "r1")
        old_entry = make_entry("Old - Source", "https://example.com/old", now - timedelta(days=2), "o1")
        parse_mock.return_value = SimpleNamespace(entries=[recent_entry, old_entry], get=lambda key: 200)

        articles = cast(list, get_articles_from_rss("query"))

        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, "Recent")

    @patch("core.search.feedparser.parse")
    def test_get_articles_from_rss_limit_applies(self, parse_mock):
        now = datetime.now(timezone.utc)
        entries = [
            make_entry("A - S", "https://example.com/a", now - timedelta(hours=1), "a1"),
            make_entry("B - S", "https://example.com/b", now - timedelta(hours=2), "b1"),
            make_entry("C - S", "https://example.com/c", now - timedelta(hours=3), "c1"),
        ]
        parse_mock.return_value = SimpleNamespace(entries=entries, get=lambda key: 200)

        articles = cast(list, get_articles_from_rss("query", limit=2))

        self.assertEqual(len(articles), 2)
        self.assertEqual([a.title for a in articles], ["A", "B"])


if __name__ == "__main__":
    unittest.main()
