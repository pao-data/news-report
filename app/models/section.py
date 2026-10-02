from dataclasses import dataclass


@dataclass
class Section:
    """Ordered collection of article IDs for one section.

    `Section` owns only local order within a section; it does not manage
    cross-container membership (assigned vs unassigned).
    """

    id: str
    name: str
    articles: list[str]  # of article ids

    def move_article_up(self, article_position: int) -> None:
        if article_position != 0:
            articles = self.articles
            articles.insert(article_position - 1, articles.pop(article_position))
            self.articles = articles

    def move_article_down(self, article_position: int) -> None:
        if article_position != len(self.articles) - 1:
            articles = self.articles
            articles.insert(article_position + 1, articles.pop(article_position))
            self.articles = articles

    def add_article(self, article_id: str) -> None:
        self.articles.append(article_id)

    def remove_article(self, article_id: str) -> None:
        self.articles.remove(article_id)

    def has_articles(self) -> bool:
        return True if len(self.articles) > 0 else False


# sections should have articles
# and also order of articles
