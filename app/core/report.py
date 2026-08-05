import logging
from copy import deepcopy
from datetime import date
from io import BytesIO

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docxtpl import DocxTemplate, RichText
from models.article import Article
#from newspaper import Article

logger = logging.getLogger(__name__)

# The text that separates the summary and full articles sections in the template document.
SUPERSECTION_DIVIDER = "FULL ARTICLES"


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


def _xml_text(element) -> str:
    return "".join(node.text or "" for node in element.iter(qn("w:t")))


def _add_bookmark(paragraph, bookmark_name: str, bookmark_id: int) -> None:
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bookmark_id))
    start.set(qn("w:name"), bookmark_name)

    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bookmark_id))

    paragraph._p.insert(0, start)
    paragraph._p.append(end)


def _set_anchor_on_text(
    paragraph, target_text: str, anchor: str, tooltip: str | None = None
) -> bool:
    """
    Update the anchor for target_text in a paragraph.
    If target_text is plain run text, wrap that run in an internal hyperlink.
    """
    for child in list(paragraph._p):
        tag = child.tag.split("}")[-1]
        text = _xml_text(child)
        if target_text not in text:
            continue

        if tag == "hyperlink":
            child.set(qn("w:anchor"), anchor)
            if tooltip:
                child.set(qn("w:tooltip"), tooltip)
            return True

        if tag == "r":
            hyperlink = OxmlElement("w:hyperlink")
            hyperlink.set(qn("w:anchor"), anchor)
            if tooltip:
                hyperlink.set(qn("w:tooltip"), tooltip)
            hyperlink.append(deepcopy(child))
            paragraph._p.replace(child, hyperlink)
            return True

    return False


def _build_section_links(doc, section_names: list[str]) -> dict[str, dict]:
    """
    For the given section names, build a dictionary of document locations to be
    used for internal navigation link hyperlinks and anchors.
    """
    section_links = {
        name: {
            "summary_heading": None,
            "full_heading": None,
            "summary_nav_paragraphs": [],
            "full_nav_paragraphs": [],
        }
        for name in section_names
    }

    region = "summary"
    summary_idx = 0
    full_idx = 0
    current_summary_section = None
    current_full_section = None

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue

        if text == SUPERSECTION_DIVIDER:
            region = "full"
            continue

        if region == "summary":
            if summary_idx < len(section_names) and text == section_names[summary_idx]:
                section_links[text]["summary_heading"] = paragraph
                current_summary_section = text
                summary_idx += 1
                continue

            if current_summary_section and ("Full Articles" in text or "Back to Top" in text):
                section_links[current_summary_section]["summary_nav_paragraphs"].append(paragraph)

        else:
            if full_idx < len(section_names) and text == section_names[full_idx]:
                section_links[text]["full_heading"] = paragraph
                current_full_section = text
                full_idx += 1
                continue

            if current_full_section and "Back to Summaries" in text:
                section_links[current_full_section]["full_nav_paragraphs"].append(paragraph)

    return section_links


def _add_internal_section_navigation(rendered_docx: BytesIO, section_names: list[str]) -> BytesIO:
    rendered_docx.seek(0)
    doc = Document(rendered_docx)
    section_links = _build_section_links(doc, section_names)

    bookmark_id = 1
    for idx, name in enumerate(section_names):
        section_info = section_links[name]
        summary_heading = section_info["summary_heading"]
        full_heading = section_info["full_heading"]
        if summary_heading is None or full_heading is None:
            logger.warning(
                "Skipping section navigation for '%s': missing heading in summary or full section.",
                name,
            )
            continue

        summary_anchor = f"summary_section_{idx}"
        full_anchor = f"full_section_{idx}"
        _add_bookmark(summary_heading, summary_anchor, bookmark_id)
        bookmark_id += 1
        _add_bookmark(full_heading, full_anchor, bookmark_id)
        bookmark_id += 1

        for nav_paragraph in section_info["summary_nav_paragraphs"]:
            _set_anchor_on_text(
                nav_paragraph,
                "Full Articles",
                full_anchor,
                tooltip=f"Go to Full Articles for {name}.",
            )
            _set_anchor_on_text(
                nav_paragraph,
                "Back to Top",
                "_top",
                tooltip="Go to top of document.",
            )

        for nav_paragraph in section_info["full_nav_paragraphs"]:
            _set_anchor_on_text(
                nav_paragraph,
                "Back to Summaries",
                summary_anchor,
                tooltip=f"Go to Summaries for {name}.",
            )

    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output


def get_article_context(article: Article, doc: DocxTemplate) -> dict:
    article_context = {}

    if article.url:
        title_with_link = RichText()
        title_with_link.add(
            article.title,
            url_id=doc.build_url_id(article.url),
            font="Arial",
            size=2 * 10,  # font size is represented in half-points, so this is font size 10
            bold=True,
            underline=True,
            color="#0000EE",
        )
    else:
        title_with_link = article.title

    source = article.source or "no source identified"

    #author = article.author or "no author identified"

    date = article.date_published_string or "unknown publication date"

    full_text = (
        prettify_text(article.full_text)
        if article.full_text
        else "no text found (perhaps due to bot blocking by the website)"
    )
    summary = (
        summarize_article(article.full_text)
        if article.full_text
        else "no text found to summarize (perhaps due to bot blocking by the website)"
    )

    article_context = {
        "title_with_link": title_with_link,
        "source": source,
     #   "author": author,
        "full_text": full_text,
        "summary": summary,
        "date": date,
    }
#        "summary": summary, <Removed from article_context due to formatting issues>

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
        "sections": sections_doccontext,
    }
    return context


def generate_document(layout, template):
    """
    template:    Path or file-like. Template word doc to use for report document generation.
    layout:      Layout object. The data used to fill in the template.
    """
    doc = DocxTemplate(template)
    section_names = [section.name for section in layout.get_ordered_sections()]
    context = generate_doc_context(layout, doc)
    doc.render(context, autoescape=True)

    # Save intermediate document to an in-memory buffer.
    rendered_buffer = BytesIO()
    doc.save(rendered_buffer)

    return _add_internal_section_navigation(rendered_buffer, section_names)


# if __name__ == "__main__":
#     articles = []
#     template_path = "basic_template.docx"
#     context = generate_doc_context(articles)
#     buffer = generate_document(template_path, context)
#     with open("output_document.docx", "wb") as f:
#         f.write(buffer.getvalue())
