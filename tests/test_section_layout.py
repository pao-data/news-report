import unittest
from datetime import datetime, timezone

from path_setup import ensure_app_on_path

ensure_app_on_path()
from models.article import Article
from models.layout import Layout
from models.section import Section


def make_article(article_id: str) -> Article:
    return Article(
        id=article_id,
        title=f"title-{article_id}",
        source="source",
        published=datetime(2026, 7, 8, 0, 0, tzinfo=timezone.utc),
        url=None,
        google_url=f"https://example.com/{article_id}",
        full_text=None,
    )


class TestSection(unittest.TestCase):
    def test_move_article_up_and_down(self):
        section = Section(id="s1", name="Section", articles=["a", "b", "c"])
        section.move_article_up(2)
        self.assertEqual(section.articles, ["a", "c", "b"])
        section.move_article_down(0)
        self.assertEqual(section.articles, ["c", "a", "b"])

    def test_has_articles(self):
        section = Section(id="s1", name="Section", articles=[])
        self.assertFalse(section.has_articles())
        section.add_article("a1")
        self.assertTrue(section.has_articles())


class TestLayout(unittest.TestCase):
    def test_init_creates_ordered_sections(self):
        layout = Layout(["One", "Two"])
        ordered = layout.get_ordered_sections()
        self.assertEqual([s.name for s in ordered], ["One", "Two"])
        self.assertEqual(layout.unassigned_articles, [])

    def test_add_new_articles_deduplicates_by_id(self):
        layout = Layout(["One"])
        a1 = make_article("a1")
        a1_dupe = make_article("a1")
        layout.add_new_articles([a1, a1_dupe])
        self.assertEqual(layout.unassigned_articles, ["a1"])
        self.assertIn("a1", layout.articles)

    def test_assign_unassign_and_delete_unassigned_article(self):
        layout = Layout(["One"])
        section_id = layout.section_order[0]
        article = make_article("a1")
        layout.add_new_articles([article])

        layout.assign_article("a1", section_id)
        self.assertEqual(layout.unassigned_articles, [])
        self.assertEqual(layout.sections[section_id].articles, ["a1"])

        layout.unassign_article("a1", section_id)
        self.assertEqual(layout.sections[section_id].articles, [])
        self.assertEqual(layout.unassigned_articles, ["a1"])

        layout.delete_unassigned_article("a1")
        self.assertEqual(layout.unassigned_articles, [])
        self.assertNotIn("a1", layout.articles)

    def test_assign_requires_known_unassigned_article(self):
        layout = Layout(["One"])
        section_id = layout.section_order[0]

        with self.assertRaises(ValueError):
            layout.assign_article("missing", section_id)

        article = make_article("a1")
        layout.add_new_articles([article])
        layout.assign_article("a1", section_id)
        with self.assertRaises(ValueError):
            layout.assign_article("a1", section_id)

    def test_unassign_requires_section_membership(self):
        layout = Layout(["One"])
        section_id = layout.section_order[0]
        article = make_article("a1")
        layout.add_new_articles([article])

        with self.assertRaises(ValueError):
            layout.unassign_article("a1", section_id)

        layout.assign_article("a1", section_id)
        layout.unassign_article("a1", section_id)
        with self.assertRaises(ValueError):
            layout.unassign_article("a1", section_id)

    def test_article_membership_is_exactly_one_place(self):
        layout = Layout(["One"])
        section_id = layout.section_order[0]
        article = make_article("a1")
        layout.add_new_articles([article])

        self.assertIn("a1", layout.unassigned_articles)
        self.assertNotIn("a1", layout.sections[section_id].articles)

        layout.assign_article("a1", section_id)
        self.assertNotIn("a1", layout.unassigned_articles)
        self.assertIn("a1", layout.sections[section_id].articles)

        layout.unassign_article("a1", section_id)
        self.assertIn("a1", layout.unassigned_articles)
        self.assertNotIn("a1", layout.sections[section_id].articles)
        layout._assert_membership_invariants()

    def test_invariants_reject_orphaned_article_membership(self):
        layout = Layout(["One"])
        article = make_article("a1")
        layout.add_new_articles([article])
        layout.unassigned_articles.remove("a1")

        with self.assertRaises(ValueError):
            layout._assert_membership_invariants()

    def test_delete_unassigned_article_non_unassigned_is_noop(self):
        layout = Layout(["One"])
        article = make_article("a1")
        layout.add_new_articles([article])
        layout.delete_unassigned_article("missing-id")
        self.assertEqual(layout.unassigned_articles, ["a1"])
        self.assertIn("a1", layout.articles)

    def test_reorder_section_happy_path(self):
        layout = Layout(["One", "Two", "Three"])
        layout.reorder_section(0, 2)
        names = [s.name for s in layout.get_ordered_sections()]
        self.assertEqual(names, ["Two", "Three", "One"])

    def test_unfinished_methods_currently_return_none(self):
        layout = Layout(["One"])
        self.assertIsNone(layout.delete_section())
        self.assertIsNone(layout.move_article("a1", "from", "to"))


if __name__ == "__main__":
    unittest.main()
