import streamlit as st
import logging

import core.search
import core.extraction

from models.article import Article

logger = logging.getLogger(__name__)

def show_search_section():
    st.markdown("### Search Google News")
    query = st.text_input("Search query:")

    if st.button("Search!"):
        logger.info(f"User searched: {query}")
        st.session_state.show_search_results = False
        with st.spinner("Searching for news articles..."):
            articles = core.search.get_articles_from_rss(query)
            articles = [core.extraction.enrich_url(article) for article in articles]
            articles = [core.extraction.enrich_full_text(article) for article in articles]

            st.session_state.layout.add_new_articles(articles)
            st.session_state.show_search_results = True
        st.rerun()

    if st.session_state.show_search_results:
        display_search_results()

def display_search_results():
    layout = st.session_state.layout
    articles = layout.get_unassigned_articles()
    if not articles:
        st.write("No articles found for your search query.")
    for article in articles:
        title = article.title
        source = article.source
        published = f"{article.date_published_string} {article.time_published_string}"
        url = article.url
        text = article.full_text
        preview_text = get_preview_text(
            text,
            missing_text_message="Text for this article could not be found. It is possible access was refused because of bot-detection measures."
        )
        with st.expander(f"***{title}*** ({source})"):
            st.write(f"Published:\t{published}")
            st.write(f"Link:\t{url}")
            st.write(f"{preview_text}")
            selectbox_key = f"selectbox_add_unassigned_article_to_section_{article.id}"
            r = st.selectbox(
                "Add article to report:",
                index=None,
                placeholder="Choose a section to add the article to.",
                options=layout.section_order,
                format_func=lambda section_id: layout.sections[section_id].name,
                key=selectbox_key,
                on_change=assign_article_on_selection,
                kwargs={
                    "article_id": article.id,
                    "selectbox_key": selectbox_key
                },
            )
            st.write(r)

def assign_article_on_selection(article_id, selectbox_key):
    st.session_state.layout.assign_article(
        article_id=article_id,
        to_id=st.session_state[selectbox_key]
    )
    st.rerun()


def get_preview_text(text: str | None, missing_text_message: str, max_words=100) -> str:
    if not text:
        return missing_text_message
    else:
        words_list = text.split()
        if len(words_list) <= max_words:
            return " ".join(words_list)
        else:
            n = int(max_words/2)
            # Use double space before newline since it's needed for html rendering used by st.write()
            shorted_preview = " ".join(words_list[:n]) + "  \n...  \n" + " ".join(words_list[-n:])
            return shorted_preview