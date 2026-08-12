import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from path_setup import ensure_app_on_path

ensure_app_on_path()
from models.article import Article
from models.layout import Layout
from models.section import Section
from utils.config import DEFAULT_SECTION_NAMES, load_default_section_names


def make_article(article_id: str) -> Article:
    return Article(
        id=article_id,
        title=f"title-{article_id}",
        source="source",
        author="author",
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

    def test_delete_unassigned_article_non_unassigned_raises(self):
        layout = Layout(["One"])
        article = make_article("a1")
        layout.add_new_articles([article])
        with self.assertRaises(ValueError):
            layout.delete_unassigned_article("missing-id")
        self.assertEqual(layout.unassigned_articles, ["a1"])
        self.assertIn("a1", layout.articles)

    def test_reorder_section_happy_path(self):
        layout = Layout(["One", "Two", "Three"])
        layout.reorder_section(0, 2)
        names = [s.name for s in layout.get_ordered_sections()]
        self.assertEqual(names, ["Two", "Three", "One"])

    def test_reorder_section_invalid_index_raises(self):
        layout = Layout(["One", "Two"])
        with self.assertRaises(ValueError):
            layout.reorder_section(-1, 1)
        with self.assertRaises(ValueError):
            layout.reorder_section(0, 5)

    def test_unfinished_methods_raise_not_implemented(self):
        layout = Layout(["One"])
        with self.assertRaises(NotImplementedError):
            layout.move_article("a1", "from", "to")

    def test_init_rejects_duplicate_section_names(self):
        with self.assertRaises(ValueError) as cm:
            Layout(["Tech", "Sports", "Tech"])
        self.assertIn("similar name", str(cm.exception))

    def test_init_rejects_case_insensitive_duplicates(self):
        with self.assertRaises(ValueError) as cm:
            Layout(["Tech", "Sports", "tech"])
        self.assertIn("similar name", str(cm.exception))

    def test_init_rejects_whitespace_duplicates(self):
        with self.assertRaises(ValueError) as cm:
            Layout(["Tech", " Tech ", "Sports"])
        self.assertIn("similar name", str(cm.exception))

    def test_add_section_rejects_duplicate(self):
        layout = Layout(["Tech"])
        with self.assertRaises(ValueError) as cm:
            layout.add_section("Tech")
        self.assertIn("similar name", str(cm.exception))

    def test_add_section_rejects_case_insensitive_duplicate(self):
        layout = Layout(["Tech"])
        with self.assertRaises(ValueError) as cm:
            layout.add_section("tech")
        self.assertIn("similar name", str(cm.exception))

    def test_add_section_rejects_whitespace_duplicate(self):
        layout = Layout(["Tech"])
        with self.assertRaises(ValueError) as cm:
            layout.add_section(" Tech ")
        self.assertIn("similar name", str(cm.exception))

    def test_add_section_preserves_case(self):
        layout = Layout(["TeCh"])
        sections = layout.get_ordered_sections()
        self.assertEqual(sections[0].name, "TeCh")

    def test_add_section_trims_whitespace(self):
        layout = Layout([])
        layout.add_section("  Tech  ")
        sections = layout.get_ordered_sections()
        self.assertEqual(sections[0].name, "Tech")

    def test_add_section_rejects_empty_name(self):
        layout = Layout([])
        with self.assertRaises(ValueError) as cm:
            layout.add_section("   ")
        self.assertIn("empty", str(cm.exception))

    def test_delete_section_empty_section(self):
        layout = Layout(["One", "Two", "Three"])
        section_id = layout.section_order[1]
        layout.delete_section(section_id)
        names = [s.name for s in layout.get_ordered_sections()]
        self.assertEqual(names, ["One", "Three"])
        self.assertEqual(len(layout.sections), 2)

    def test_delete_section_with_articles_moves_to_unassigned(self):
        layout = Layout(["One", "Two"])
        section_id = layout.section_order[0]
        a1 = make_article("a1")
        a2 = make_article("a2")
        layout.add_new_articles([a1, a2])
        layout.assign_article("a1", section_id)
        layout.assign_article("a2", section_id)

        self.assertEqual(layout.sections[section_id].articles, ["a1", "a2"])
        self.assertEqual(layout.unassigned_articles, [])

        layout.delete_section(section_id)

        self.assertEqual(len(layout.sections), 1)
        self.assertNotIn(section_id, layout.sections)
        self.assertEqual(layout.unassigned_articles, ["a1", "a2"])
        layout._assert_membership_invariants()

    def test_delete_section_removes_from_normalized_names(self):
        layout = Layout(["Tech", "Sports"])
        section_id = layout.section_order[0]
        section_name = layout.sections[section_id].name

        layout.delete_section(section_id)

        layout.add_section("Tech")
        self.assertEqual(len(layout.sections), 2)

    def test_delete_section_unknown_id_raises(self):
        layout = Layout(["One"])
        with self.assertRaises(ValueError) as cm:
            layout.delete_section("unknown-id")
        self.assertIn("Unknown section ID", str(cm.exception))

    def test_delete_section_maintains_invariants(self):
        layout = Layout(["One", "Two", "Three"])
        section_id = layout.section_order[1]
        a1 = make_article("a1")
        layout.add_new_articles([a1])
        layout.assign_article("a1", section_id)

        layout.delete_section(section_id)

        layout._assert_membership_invariants()


class TestConfig(unittest.TestCase):
    def test_load_default_section_names_from_config(self):
        expected_names = ["Alpha", "Bravo", "Charlie"]
        with patch(
            "utils.config.load_config", return_value={"defaults": {"section_names": expected_names}}
        ):
            self.assertEqual(load_default_section_names(), expected_names)

    def test_load_default_section_names_falls_back_for_invalid_config(self):
        invalid_configs = [
            {},
            {"defaults": {}},
            {"defaults": {"section_names": []}},
            {"defaults": {"section_names": "not-a-list"}},
            {"defaults": {"section_names": [2348, 123]}},
            {"defaults": {"section_names": ["   ", " "]}},
        ]
        for invalid_config in invalid_configs:
            with patch("utils.config.load_config", return_value=invalid_config):
                self.assertEqual(load_default_section_names(), DEFAULT_SECTION_NAMES)

    def test_load_default_section_names_rejects_exact_duplicates(self):
        duplicate_config = {"defaults": {"section_names": ["Tech", "Sports", "Tech"]}}
        with patch("utils.config.load_config", return_value=duplicate_config):
            with self.assertRaises(ValueError) as cm:
                load_default_section_names()
            self.assertIn("Duplicate section name", str(cm.exception))

    def test_load_default_section_names_rejects_case_insensitive_duplicates(self):
        duplicate_config = {"defaults": {"section_names": ["Tech", "Sports", "tech"]}}
        with patch("utils.config.load_config", return_value=duplicate_config):
            with self.assertRaises(ValueError) as cm:
                load_default_section_names()
            self.assertIn("Duplicate section name", str(cm.exception))

    def test_load_default_section_names_rejects_whitespace_duplicates(self):
        duplicate_config = {"defaults": {"section_names": ["Tech", " Tech ", "Sports"]}}
        with patch("utils.config.load_config", return_value=duplicate_config):
            with self.assertRaises(ValueError) as cm:
                load_default_section_names()
            self.assertIn("Duplicate section name", str(cm.exception))

    def test_load_default_section_names_preserves_case(self):
        config = {"defaults": {"section_names": ["TeCh", "SpOrTs"]}}
        with patch("utils.config.load_config", return_value=config):
            names = load_default_section_names()
            self.assertEqual(names, ["TeCh", "SpOrTs"])


if __name__ == "__main__":
    unittest.main()
