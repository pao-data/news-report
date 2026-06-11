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

    sections: dict[str, Section] # sections by id
    section_order: list[str] # order of sections by id
    articles: dict[str, Article] # articles by id
    unassigned_articles: list[str] # list of unassigned articles, in display order, by id

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

    def reorder_section(self, from_position, to_position):
        section_order = self.section_order
        if not(0 <= from_position < len(section_order)):
            ValueError("Invalid index for from_position.")
        if not(0 <= to_position < len(section_order)):
            ValueError("Invalid index for to_position.")
        section_to_move = section_order.pop(from_position)
        section_order.insert(to_position, section_to_move)
        self.section_order = section_order

    def _(self, positions_to_swap):
        if len(positions_to_swap) != 2:
            ValueError("positions_to_swap must be a tuple of length 2.")
        i, j = positions_to_swap
        section_order = self.section_order
        section_order[i], section_order[j] = section_order[j], section_order[i]
        self.section_order = section_order

    def get_ordered_section_names(self):
        return [self.sections[section_id].name for section_id in self.section_order]

    def add_new_articles(self, articles: list[Article]):
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