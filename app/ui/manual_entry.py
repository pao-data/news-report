import core.extraction
import logging
import streamlit as st
import ui.state

from models.article import Article

logger = logging.getLogger(__name__)

m_articles          = []
m_enriched_articles = []
unique_enriched_articles = []
    
def show_manual_entry_section():
    st.header("Additional Articles")
    st.write("_Add additional links here to include in the report. Please input 1 URL at a time._")

    st.text_input(
        " ",
        key="new_url_label",
        placeholder="Ex: https://www.example.com",
        label_visibility="collapsed",
        on_change=add_manual_entry_to_articles,
        kwargs={"widget_key": "new_url_label"}
    )

    # Show manually entered articles
    if ui.state.get_show_manual_results():
        st.subheader("Processed Articles")
        st.write("_Scroll to see more articles._")
        with st.container(height=250):
            display_manual_results()

def add_manual_entry_to_articles(widget_key):
    # assign user entered text to url variable before clearing input
    url = st.session_state[widget_key]
    st.session_state[widget_key] = ""  # Clear the input

    new_manual_entry = Article.from_manual_entry(url)
    new_manual_entry = core.extraction.enrich_url(new_manual_entry)
    new_manual_entry = core.extraction.enrich_author(new_manual_entry)
    new_manual_entry = core.extraction.enrich_full_text(new_manual_entry)
    m_enriched_articles.append(new_manual_entry)

    ui.state.get_layout().add_new_manual_articles(m_enriched_articles)
    ui.state.set_show_manual_results(True)

def display_manual_results():
    layout = ui.state.get_layout()
    articles = layout.get_unassigned_manual_articles()
    if not articles:
        st.write("No articles were manually entered.")
    for article in articles:
        title = article.title
        source = article.source
        published = f"{article.date_published_string}"
        url = article.url if article.url else article.google_url
        if not article.url:
            missing_text_message = """Text for this article could not be obtained because we could not decode the link provided.
            Sometimes this can happen if we've recently tried to decode too many links in a short period of time.
            Please try following the link in your browser and pasting the page's source HTML into the HTML Conversion Tool."""
        else:
            missing_text_message = """Text for this article could not be found.
            It is possible access was refused because of bot-detection measures, but other reasons are also possible."""
        text = article.full_text
        preview_text = get_preview_text(text, missing_text_message=missing_text_message)
        with st.expander(f"***{title}*** ({source})"):
            st.write(f"Published:\t{published}")
            st.write(f"Link:\t{url}")
            st.write(f"{preview_text}")
            selectbox_key = f"selectbox_add_unassigned_article_to_section_manual{article.id}"
            r = st.selectbox(
                "Add article to report:",
                index=None,
                placeholder="Choose a section to add the article to.",
                options=layout.section_order,
                format_func=lambda section_id: layout.sections[section_id].name,
                key=selectbox_key,
                on_change=assign_article_on_selection,
                kwargs={"article_id": article.id, "selectbox_key": selectbox_key},
            )
            st.button(
                "Delete article entirely (cannot be undone)",
                icon=":material/delete:",
                key=f"fully_delete_unassigned_article_manual{article.id}",
                on_click=layout.delete_unassigned_manual_article,
                kwargs={"article_id": article.id},
            )

def assign_article_on_selection(article_id, selectbox_key):
    ui.state.get_layout().assign_article(
        article_id=article_id, to_id=st.session_state[selectbox_key]
    )

def get_preview_text(text: str | None, missing_text_message: str, max_words=100) -> str:
    if not text:
        return missing_text_message
    else:
        words_list = text.split()
        if len(words_list) <= max_words:
            return " ".join(words_list)
        else:
            n = int(max_words / 2)
            # Use double space before newline since it's needed for html rendering used by st.write()
            shortened_preview = " ".join(words_list[:n]) + "  \n...  \n" + " ".join(words_list[-n:])
            return shortened_preview