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

    full_text = prettify_text(article.full_text) if article.full_text else "no text found (perhaps due to bot blocking by the website)"
    summary = summarize_article(article.full_text) if article.full_text else "no text found to summarize (perhaps due to bot blocking by the website)"

    article_context = {
        "title_with_link": title_with_link,
        "source": source,
        "full_text": full_text,
        "summary": summary,
        "date": date,
    }

    return article_context

def generate_doc_context(layout, doc):
    today = date.today()
    section_objects = layout.get_ordered_sections()
    sections_doccontext = []
    for section_obj in section_objects:
        section_cxt = {}
        section_cxt["name"] = section_obj.name
        articles_doccontext = []
        for article_id in section_obj.articles:
            article_obj = layout.articles[article_id]
            article_cxt = get_article_context(article_obj, doc)
            articles_doccontext.append(article_cxt)
        section_cxt["articles"] = articles_doccontext
        sections_doccontext.append(section_cxt)

    context = {
        "report_date": {
            "day": today.day,
            "month": today.strftime("%B"),
            "year": today.year,
        },
        "sections": sections_doccontext
    }
    return context

def generate_document(layout, template):
    """
    template:    Path or file-like. Template word doc to use for report document generation.
    layout:      Layout object. The data used to fill in the template.
    """
    doc = DocxTemplate(template)
    context = generate_doc_context(layout, doc)
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
