import logging
import time

from docxtpl import DocxTemplate, RichText
from io import BytesIO

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

def separate_title_and_source(title_source_string):
    parts = title_source_string.split(" - ")

    if len(parts) != 2:
        logger.warning(
            "Expected 2 parts when splitting the title element from the rss feed into title and source,"
            f"got {len(parts)}: {title_source_string}",
        )

    if len(parts) == 1:
        title = parts[0]
        source = ""
    elif len(parts) == 2:
        title, source = parts
    else:
        # Making the assumption that the extra " - " would be in the title rather than the source.
        source = parts[-1]
        title = " - ".join(parts[:-1])

    return title, source

def get_article_context(article, doc):
    article_context = {}

    title, source = separate_title_and_source(article["title"])
    title_with_link = RichText()
    title_with_link.add(
        title,
        url_id=doc.build_url_id(article["url"]),
        bold=True,
        underline=True,
        color="#0000EE",
    )
    article_context["title_with_link"] = title_with_link
    article_context["source"] = source

    article_context["full_text"] = prettify_text(article["text"])
    article_context["summary"] = summarize_article(article["text"])

    article_context["date"] = time.strftime("%B %d, %Y", article["published_datetime"])
    return article_context

def generate_doc_context(articles, doc):
    context = {
        "report_date": {
            "day": 20,
            "month": "October",
            "year": 2026,
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
