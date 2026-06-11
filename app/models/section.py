from dataclasses import dataclass

@dataclass
class Section:
    name: str
    articles: list[str] # of article ids

    def move_article_up(self, article_position):
        if article_position != 0:
            articles = self.articles
            articles.insert(
                article_position-1,
                articles.pop(article_position)
            )
            self.articles = articles

    def move_article_down(self, article_position):
        if article_position != len(self.articles)-1:
            articles = self.articles
            articles.insert(
                article_position+1,
                articles.pop(article_position)
            )
            self.articles = articles

    def add_article(self, article_id):
        self.articles.append(article_id)

    def remove_article():
        ...


# sections should have articles
# and also order of articles