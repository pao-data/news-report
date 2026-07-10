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

    def add_section(self, section_name: str) -> None:
        section_id = str(uuid.uuid4())
        self.sections[section_id] = Section(name=section_name, articles=[], id=section_id)
        self.section_order.append(section_id)

    def delete_section(self) -> None:
        """
        Move all articles in section to unassigned, then
        remove section from the Layout
        """
        ...

    def reorder_section(self, from_position: int, to_position: int) -> None:
        section_order = self.section_order
        if not(0 <= from_position < len(section_order)):
            ValueError("Invalid index for from_position.")
        if not(0 <= to_position < len(section_order)):
            ValueError("Invalid index for to_position.")
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

    def move_article(self, article_id: str, from_id: str, to_id: str) -> None:
        """Move article from one section to another."""
        ...
    
    def assign_article(self, article_id: str, to_id: str) -> None:
        """Move an article from unassigned into a target section."""
        to_section = self.sections[to_id]
        self.unassigned_articles.remove(article_id)
        to_section.add_article(article_id)

    def unassign_article(self, article_id: str, from_id: str) -> None:
        """Move an article from a section back to unassigned."""
        from_section = self.sections[from_id]
        from_section.remove_article(article_id)
        self.unassigned_articles.append(article_id)

    def delete_unassigned_article(self, article_id: str) -> None:
        """Fully delete an unassigned article."""
        if not article_id in self.unassigned_articles:
            ValueError(
                f"Attempt to delete article that is not in unassigned articles.\n\tArticle id: {article_id}"
            )
            return
        self.unassigned_articles.remove(article_id)
        del self.articles[article_id]


    

# for article in section:
# - display container
# - display "move to" or "add to" depending on status
# - display drop down where defeault selection is current container

# not in report, query results