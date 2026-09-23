import difflib
import logging
import re
from copy import deepcopy
from datetime import date
from io import BytesIO

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docxtpl import DocxTemplate, RichText
from models.article import Article

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

def split_text_with_newline(text):

    words = []
    if text:
        parts = re.split(r'(\n)', text)
        
        for p in parts:
            if p == "":
                continue
            if p == "\n":
                words.extend("\n\n") # prettify output
            else:
                words.extend(p.split())

    return words

def add_to_richtext(rt_obj, text_to_add, highlight_color=None):
    rt_obj.add(
        text_to_add,
        font = "Arial",
        size = 2 * 10,
        highlight = highlight_color,
        color = "000000"
    )
    return rt_obj

def highlight_artifacts(text_original, text_precision):

    filler_phrases = [["subscribe", "now"], ["subscribe", "here"], ["sign", "up"], ["mailing", "list"], ["more", "stories", "like", "this"], ["upgrade", "to", "premium"], ["donate", "to", "support"], 
                      ["share", "this", "article"], ["tell", "your", "friends"], ["email", "us", "at"], ["follow", "us", "on"], ["leave", "a", "comment"], ["all", "rights", "reserved"],
                      ["reproduction", "without", "permission", "is", "prohibited"], ["terms", "and", "conditions", "apply"], ["see", "our", "privacy", "policy"], 
                      ["click", "here", "to", "read", "the", "full", "article"], ["return", "to", "homepage"], ["recommended", "for", "you"], ["trending", "now"], 
                      ["get", "the", "most", "important", "news", "from"], ["share", "with", "us", "your", "feedback"]]

    if text_original:
        full_text_with_highlight = RichText()
        
        list_of_words_original = split_text_with_newline(text_original)
        list_of_words_precision = split_text_with_newline(text_precision)

        d = difflib.Differ()

        # text_diff is a list that outputs "- " as a prefix to words that are found in original but not in precision 
        text_diff = list(d.compare(list_of_words_original, list_of_words_precision))

        # d.compare() adds 2 characters as prefix to each word, "- " if in og not in precision, "  " if found in both
        text_diff = [word.replace("  ", "") for word in text_diff]
        print(f"text_diff: {text_diff}")

        # TODO: test to see how hyphens react here replace "- " with "*" 
        # text_diff = [word.replace("- ", "*") for word in text_diff]

        # list_of_words = split_text_with_newline(text)

        i = 0
        while i < len(text_diff):
            for phrase in filler_phrases:
                phrase_len = len(phrase)

                # To find a filler phrase, all words in the phrase must be present in the text
                num_matching_words = 0

                # Iterate through the words in the phrase
                for j in range(phrase_len):
                    # Compare the next word in the text to the next word in the phrase, add to counter
                    try:
                        if text_diff[i+j].lower() == phrase[j]:
                            num_matching_words += 1
                    except:
                        break # end of text

                # if the entire phrase is found in the text, highlight the phrase
                if phrase_len == num_matching_words:
                    for k in range(phrase_len):
                        # if this word is the last in the phrase, do not add a trailing highlighted space
                        if k == phrase_len-1: 
                            full_text_with_highlight = add_to_richtext(full_text_with_highlight, text_diff[i+k], highlight_color = "#FFFF00")
                            full_text_with_highlight = add_to_richtext(full_text_with_highlight, " ") 
                        else:
                            full_text_with_highlight = add_to_richtext(full_text_with_highlight, text_diff[i+k] + " ", highlight_color = "#FFFF00")

                    # this phrase as been added to the report, skip in outer loop
                    i += phrase_len
                    # do not need to look at other phrases, break loop
                    break
            if "\n" in text_diff[i][2:]:
                full_text_with_highlight = add_to_richtext(full_text_with_highlight, text_diff[i][2:])
                i += 1
            elif "\n" in text_diff[i]:
                full_text_with_highlight = add_to_richtext(full_text_with_highlight, text_diff[i])
                i += 1
            elif "- " == text_diff[i][:2]:
                full_text_with_highlight = add_to_richtext(full_text_with_highlight, text_diff[i][2:], highlight_color = "#FFFF00")
                # if the next word needs to be highlighted, add a highlighted space next
                try:
                    if "- " == text_diff[i+1][:2]:
                        full_text_with_highlight = add_to_richtext(full_text_with_highlight, " ", highlight_color = "#FFFF00")
                except: 
                    pass # if last word in the text, don't do anything
                i += 1
            else:
                full_text_with_highlight = add_to_richtext(full_text_with_highlight, text_diff[i] + " ")    
                i += 1    
                
        full_text = full_text_with_highlight
    else:
        full_text = "no text found (perhaps due to bot blocking by the website)"

    return full_text


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

    author = article.author or "no author identified"

    date = article.date_published_string or "unknown publication date"

    full_text = highlight_artifacts(article.full_text, article.full_text_precision)

    # TODO - remove, if do not need to revert to OG
    # full_text = (
    #     prettify_text(article.full_text)
    #     if article.full_text
    #     else "no text found (perhaps due to bot blocking by the website)"
    # )

    #summary = (
    #    summarize_article(article.full_text)
    #    if article.full_text
    #    else "no text found to summarize (perhaps due to bot blocking by the website)"
    #)

    article_context = {
        "title_with_link": title_with_link,
        "source": source,
        "author": author,
        "full_text": full_text,
        "date": date,
    }
#        "summary": summary, <Removed from article_context (above) due to summary formatting issues>

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
