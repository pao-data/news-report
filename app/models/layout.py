import uuid

from models.section import Section
from models.article import Article


class Layout:
    # sections: list of all the section names NOTE sections have inherent order
    # dict of articles by ID? or list of tuples??
    # articles

    # membership: 
    # unassigned
    # TODO articles should have order also

    # methods:
    # - move an article to a new section
    # - add a section
    # - change section orders

    sections: dict[str, Section]
    section_order: list[str]
    articles: dict[str, Article]
    unassigned_articles: list[str]

    def __init__(self, section_names: list[str]):
        self.sections = {}
        self.section_order = []
        for section_name in section_names:
            self.add_section(section_name)
        # Layouts should have no articles upon initialization
        self.articles = {}
        self.unassigned_articles = []

    def add_section(self, section_name: str):
        section_id = str(uuid.uuid4())
        self.sections[section_id] = Section(name=section_name, articles=[])
        self.section_order.append(section_id)

    def delete_section():
        """
        Move all articles in section to unassigned, then
        remove section from the Layout
        """
        ...

    def reorder_sections():
        ...

    def add_articles_to_layout(self, articles: list[Article]):
        """Add new articles to the layout. All new articles start as unassigned to a section."""
        for article in articles:
            if article.id not in self.articles:
                self.unassigned_articles.append(article.id)
                self.articles[article.id] = article

    def move_article(article_id, from_id, to_id):
        """Move article from one section to another."""
        ...
    
    def assign_article(self, article_id, to_id):
        """Move an unassigned article to a section."""
        to_section = self.sections[to_id]
        self.unassigned_articles.remove(article_id)
        to_section.add_article(article_id)

    def unassign_article(article_id, from_id):
        """Move an article from its section to unassigned. """
        ...

    


    

# for article in section:
# - display container
# - display "move to" or "add to" depending on status
# - display drop down where defeault selection is current container

# not in report, query results