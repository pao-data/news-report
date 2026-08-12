import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from path_setup import ensure_app_on_path

ensure_app_on_path()
from models.article import Article


class TestArticle(unittest.TestCase):
    def test_separate_title_and_source_two_parts(self):
        title, source = Article.separate_title_and_source("Headline - Reuters")
        self.assertEqual(title, "Headline")
        self.assertEqual(source, "Reuters")

    def test_separate_title_and_source_one_part(self):
        title, source = Article.separate_title_and_source("Headline only")
        self.assertEqual(title, "Headline only")
        self.assertEqual(source, "")

    def test_separate_title_and_source_many_parts(self):
        title, source = Article.separate_title_and_source("A - B - Reuters")
        self.assertEqual(title, "A - B")
        self.assertEqual(source, "Reuters")

    def test_make_article_id_prefers_entry_id(self):
        entry = {"id": "abc", "guid": "g", "link": "l", "title": "t"}
        self.assertEqual(Article.make_article_id(entry), "900150983cd24fb0d6963f7d28e17f72")

    def test_from_rss_entry_sets_expected_fields(self):
        published_parsed = (2026, 7, 8, 12, 15, 30, 0, 0, 0)
        entry = SimpleNamespace(
            link="https://news.google.com/example",
            get=lambda key, default=None: {
                "title": "Title - Source",
                "published_parsed": published_parsed,
                "id": "entry-id",
            }.get(key, default),
        )

        article = Article.from_rss_entry(entry)

        self.assertEqual(article.title, "Title")
        self.assertEqual(article.source, "Source")
        self.assertEqual(article.author, "Author")
        self.assertEqual(article.google_url, "https://news.google.com/example")
        self.assertEqual(article.url, None)
        self.assertEqual(article.full_text, None)
        self.assertEqual(article.published, datetime(2026, 7, 8, 12, 15, 30, tzinfo=timezone.utc))

    def test_format_helpers_handle_missing_published(self):
        article = Article(
            id="1",
            title="t",
            source="s",
            author="a",
            published=None,
            url=None,
            google_url="g",
            full_text=None,
        )
        self.assertEqual(article.format_published("%B %d, %Y"), "")


if __name__ == "__main__":
    unittest.main()
