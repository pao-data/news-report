import logging
from datetime import date

from docxtpl import DocxTemplate, RichText
from io import BytesIO

from models.article import Article

logger = logging.getLogger(__name__)

def prettify_text(text):
    text = text.replace("\n", "\n\n")
    return text

def summarize_article(text, min_characters=500):
    # TODO should probably replace this with a better summarization strategy at some point
    summary = ""
    for ppg in text.split("\n"):
        summary += ppg
        if len(summary) >= min_characters:
            break
        summary += "\n"
    return summary

def get_article_context(article: Article, doc: DocxTemplate) -> dict:
    article_context = {}

    if article.url:
        title_with_link = RichText()
        title_with_link.add(
            article.title,
            url_id=doc.build_url_id(article.url),
            bold=True,
            underline=True,
            color="#0000EE",
        )
    else:
        title_with_link=article.title
    
    source = article.source or "no source identified"

    date = article.date_published_string or "unknown publication date"

    article_context = {
        "title_with_link": title_with_link,
        "source": source,
        "full_text": prettify_text(article.full_text),
        "summary": summarize_article(article.full_text),
        "date": date,
    }

    return article_context

def generate_doc_context(articles, doc):
    today = date.today()
    context = {
        "report_date": {
            "day": today.day,
            "month": today.strftime("%B"),
            "year": today.year,
        },
        "sections": [
            {
                "name": "first section",
                "articles": [get_article_context(a, doc) for a in articles],
            },
            {
                "name": "second section",
                "text": "the first text for the second section!",
                "full_text": "the second text for the second section. This is longer than the first text was!\nThere was a new line character!",
            },
        ]
    }
    return context

def generate_document(articles, template):
    """
    template:    Path or file-like. Template word doc to use for report document generation.
    context:     Dict. The data used to fill in the template.
    """
    doc = DocxTemplate(template)
    context = generate_doc_context(articles, doc)
    doc.render(context)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer

# if __name__ == "__main__":
#     articles = []
#     template_path = "basic_template.docx"
#     context = generate_doc_context(articles)
#     buffer = generate_document(template_path, context)
#     with open("output_document.docx", "wb") as f:
#         f.write(buffer.getvalue())
