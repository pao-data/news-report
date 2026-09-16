import core.extraction
import logging
import streamlit as st
import ui.state

from datetime import datetime
from models.article import Article

logger = logging.getLogger(__name__)
    
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
        with st.container(height=350):
            display_manual_results()

def add_manual_entry_to_articles(widget_key):
    m_enriched_articles = []

    # assign user entered text to url variable before clearing input
    url = st.session_state[widget_key]
    # Clear the input
    st.session_state[widget_key] = ""  

    new_manual_entry = Article.from_link_entry(url)
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
        st.write("No additional articles were entered.")
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

            show_update_article_manually(article)

def show_update_article_manually(article: Article):
    with st.popover("Manually Update Details", on_change = on_popover_change, key = f"manual_detail_popover_{article.id}"):
        st.write("Please enter article information below. To save changes, press _Enter_ after each input.")
        m_title = st.text_input(label = "Title",
                                key = f"manually_added_title_{article.id}",
                                placeholder = "",
                                value = article.title)
        
        m_author = st.text_input(label = "Author(s)", 
                                 key = f"manually_added_author_{article.id}",
                                 placeholder = "",
                                 value = article.author)
        
        m_source = st.text_input(label = "Source", 
                                 key = f"manually_added_source_{article.id}",
                                 placeholder="Ex: XYZ News Source",
                                 value = article.source)

        try:
            published_strf = article.published.strftime("%Y-%m-%d")
        except:
            published_strf = None

        m_published = st.text_input(label = "Publish Date", 
                                    key = f"manually_added_date_{article.id}",
                                    placeholder="Use Format: YYYY-MM-DD",
                                    value = published_strf)

        m_full_text = st.text_area(label = "Full Article Text (Ctr+Enter to apply changes)", 
                                    key = f"manually_added_text_{article.id}",
                                    placeholder="",
                                    height = 150,
                                    value = article.full_text)

        article.title     = m_title
        article.author    = m_author
        article.source    = m_source
        try:
            article.full_text = m_full_text.replace("\n\n","\n")
        except:
            article.full_text = m_full_text
        try:
            article.published = datetime.strptime(m_published,'%Y-%m-%d')
        except:
            article.published = None
        
        st.button("Close", 
                  key = f"close_popover_button_{article.id}",
                  type = 'secondary', 
                  on_click = toggle_popover,
                  kwargs = {"article_id":article.id})

# on_change argument is necessary to update state of popover
def on_popover_change():
    pass

def toggle_popover(article_id: str):
    # closes popover, when "Close" button is selected
    st.session_state[f'manual_detail_popover_{article_id}'] = not st.session_state[f'manual_detail_popover_{article_id}']

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