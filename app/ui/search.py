import streamlit as st
import logging
from uuid import uuid4

import core.search
import core.extraction

from models.article import Article

logger = logging.getLogger(__name__)


def add_query():
    label = st.session_state.new_query_label.strip()

    if not label:
        return

    if label in st.session_state.queries:
        return

    st.session_state.queries[label] = ""

    # clear input safely
    st.session_state["new_query_label"] = ""

def show_query_form():
    st.subheader("Search Google News")

    for label in list(st.session_state.queries.keys()):
        col1, col2 = st.columns([20, 1])

        with col1:
            st.text_area(
                label=label,
                key=f"query_{label}",
                value=st.session_state.queries[label],
                height="content",
            )

        with col2:
            # vertical spacing to make button look better
            st.write("")
            st.write("")

            if st.button(
                "❌",
                key=f"delete_{label}",
                help=f"Delete {label}",
            ):
                del st.session_state.queries[label]

                # Remove widget state too
                widget_key = f"query_{label}"
                if widget_key in st.session_state:
                    del st.session_state[widget_key]

                st.rerun()

        # st.markdown("---")

    # -------------------------
    # Add new query
    # -------------------------

    col, _ = st.columns([4, 10])
    col.text_input(
        "",
        key="new_query_label",
        placeholder="➕ Add search field (Enter field name and press Enter)",
        label_visibility="collapsed",
        on_change=add_query,
    )

    # -------------------------
    # Submit all
    # -------------------------

    if st.button("Submit All", type="primary"):

        results = {}

        for label in st.session_state.queries:
            results[label] = st.session_state[f"query_{label}"]

        # Keep latest values as the source of truth
        st.session_state.queries = results

        st.success("Submitted!")

        st.subheader("Submitted Data")
        st.json(results)

def show_search_section():
    show_query_form()


    st.markdown("### Search Results")
    with st.form("search_queries"):
        query = st.text_area("Search query:", height="content")
        submitted = st.form_submit_button("Search!")
        if submitted:
            logger.info(f"User searched: {query}")
            st.session_state.show_search_results = False

            progress_text = "Searching for news articles..."
            progress_bar = st.progress(0.0, text=progress_text)
            articles = core.search.get_articles_from_rss(query)
            enriched_articles = []
            for article_index, article in enumerate(articles):
                article = core.extraction.enrich_url(article)
                article = core.extraction.enrich_full_text(article)
                enriched_articles.append(article)
                progess_value = (article_index+1)/len(articles)
                progress_bar.progress(progess_value, text=progress_text)
            progress_bar.empty()

            st.session_state.layout.add_new_articles(enriched_articles)
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

def assign_article_on_selection(article_id, selectbox_key):
    st.session_state.layout.assign_article(
        article_id=article_id,
        to_id=st.session_state[selectbox_key]
    )


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