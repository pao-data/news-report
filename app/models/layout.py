import logging
import uuid

from models.section import Section
from models.article import Article

logger = logging.getLogger(__name__)

class Layout:
    """Aggregate model for report composition.

    Invariants:
    - `articles` stores each article ID at most once.
    - An article ID should exist either in exactly one section or in
      `unassigned_articles` (never both).

    Ownership:
    - Cross-container membership changes (assigned <-> unassigned) are
      managed by `Layout` methods, not `Section`.
    """
    sections: dict[str, Section] # sections by id
    section_order: list[str] # order of sections by id
    articles: dict[str, Article] # articles by id
    unassigned_articles: list[str] # list of unassigned articles, in display order, by id

    def __init__(self, section_names: list[str]) -> None:
        self.sections = {}
        self.section_order = []
        for section_name in section_names:
            self.add_section(section_name)
        # Layouts should have no articles upon initialization
        self.articles = {}
        self.unassigned_articles = []
        self._assert_membership_invariants()

    def add_section(self, section_name: str) -> None:
        section_id = str(uuid.uuid4())
        self.sections[section_id] = Section(name=section_name, articles=[], id=section_id)
        self.section_order.append(section_id)

    def delete_section(self) -> None:
        """
        Move all articles in section to unassigned, then
        remove section from the Layout
        """
        raise NotImplementedError("Layout.delete_section is intentionally not implemented yet.")

    def reorder_section(self, from_position: int, to_position: int) -> None:
        section_order = self.section_order
        if not(0 <= from_position < len(section_order)):
            raise ValueError("Invalid index for from_position.")
        if not(0 <= to_position < len(section_order)):
            raise ValueError("Invalid index for to_position.")
        section_to_move = section_order.pop(from_position)
        section_order.insert(to_position, section_to_move)
        self.section_order = section_order

    def get_ordered_sections(self) -> list[Section]:
        return [self.sections[section_id] for section_id in self.section_order]

    def get_unassigned_articles(self) -> list[Article]:
        return [self.articles[id] for id in self.unassigned_articles]

    def add_new_articles(self, articles: list[Article]) -> None:
        """Add unseen articles into `articles` and `unassigned_articles`."""
        for article in articles:
            if article.id not in self.articles:
                self.unassigned_articles.append(article.id)
                self.articles[article.id] = article
        self._assert_membership_invariants()

    def move_article(self, article_id: str, from_id: str, to_id: str) -> None:
        """Move article from one section to another."""
        raise NotImplementedError("Layout.move_article is intentionally not implemented yet.")
    
    def assign_article(self, article_id: str, to_id: str) -> None:
        """Move an article from unassigned into a target section."""
        if article_id not in self.articles:
            raise ValueError(f"Unknown article ID: {article_id}")
        if article_id not in self.unassigned_articles:
            raise ValueError(f"Article is not currently unassigned: {article_id}")
        if to_id not in self.sections:
            raise ValueError(f"Unknown section ID: {to_id}")
        to_section = self.sections[to_id]
        if article_id in to_section.articles:
            raise ValueError(f"Article already assigned to section {to_id}: {article_id}")
        self.unassigned_articles.remove(article_id)
        to_section.add_article(article_id)
        self._assert_membership_invariants()

    def unassign_article(self, article_id: str, from_id: str) -> None:
        """Move an article from a section back to unassigned."""
        if article_id not in self.articles:
            raise ValueError(f"Unknown article ID: {article_id}")
        if from_id not in self.sections:
            raise ValueError(f"Unknown section ID: {from_id}")
        from_section = self.sections[from_id]
        if article_id not in from_section.articles:
            raise ValueError(
                f"Article is not currently assigned to section {from_id}: {article_id}"
            )
        if article_id in self.unassigned_articles:
            raise ValueError(f"Article is already unassigned: {article_id}")
        from_section.remove_article(article_id)
        self.unassigned_articles.append(article_id)
        self._assert_membership_invariants()

    def delete_unassigned_article(self, article_id: str) -> None:
        """Fully delete an unassigned article."""
        if not article_id in self.unassigned_articles:
            raise ValueError(
                f"Attempt to delete article that is not in unassigned articles.\n\tArticle id: {article_id}"
            )
        self.unassigned_articles.remove(article_id)
        del self.articles[article_id]
        self._assert_membership_invariants()

    def _assert_membership_invariants(self) -> None:
        """Validate that article membership is complete and non-overlapping."""
        membership_counts: dict[str, int] = {article_id: 0 for article_id in self.articles}

        for section in self.sections.values():
            for article_id in section.articles:
                if article_id not in self.articles:
                    raise ValueError(f"Section references unknown article ID: {article_id}")
                membership_counts[article_id] += 1

        for article_id in self.unassigned_articles:
            if article_id not in self.articles:
                raise ValueError(f"Unassigned list references unknown article ID: {article_id}")
            membership_counts[article_id] += 1

        orphaned = [article_id for article_id, count in membership_counts.items() if count == 0]
        if orphaned:
            raise ValueError(f"Article IDs without membership: {orphaned}")

        duplicated = [article_id for article_id, count in membership_counts.items() if count > 1]
        if duplicated:
            raise ValueError(f"Article IDs with multiple memberships: {duplicated}")


    

# for article in section:
# - display container
# - display "move to" or "add to" depending on status
# - display drop down where defeault selection is current container

# not in report, query results