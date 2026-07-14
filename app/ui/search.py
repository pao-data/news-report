import logging

import core.extraction
import core.search
import streamlit as st
import ui.state

logger = logging.getLogger(__name__)


def show_search_section():
    st.header("Search")

    show_query_fields()

    submitted = st.button("Search All", type="primary")

    if submitted:
        results = {}

        for label in ui.state.get_queries():
            results[label] = st.session_state[f"query_{label}"]

        # Keep latest values as the source of truth
        ui.state.set_queries(results)

        logger.info(f"User searched: {results}")
        ui.state.set_show_search_results(False)

        progress_text = "Searching for news articles..."
        progress_bar = st.progress(0.0, text=progress_text)
        articles = []
        for query in results.values():
            a = core.search.get_articles_from_rss(query)
            articles.extend(a)

        enriched_articles = []
        for article_index, article in enumerate(articles):
            logging.debug(article.google_url)
            article = core.extraction.enrich_url(article)
            article = core.extraction.enrich_full_text(article)
            enriched_articles.append(article)
            progress_value = (article_index + 1) / len(articles)
            progress_bar.progress(progress_value, text=progress_text)
        progress_bar.empty()

        ui.state.get_layout().add_new_articles(enriched_articles)
        ui.state.set_show_search_results(True)
        st.rerun()

    if ui.state.get_show_search_results():
        st.header("Results")
        st.write("_Scroll to see more results._")
        with st.container(height=500):
            display_search_results()


def show_query_fields():
    queries = ui.state.get_queries()
    for label in list(queries.keys()):
        col1, col2 = st.columns([20, 1])

        with col1:
            st.text_area(
                label=label,
                key=f"query_{label}",
                value=queries[label],
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
                queries = ui.state.get_queries()
                del queries[label]
                ui.state.set_queries(queries)

                # Remove widget state too
                widget_key = f"query_{label}"
                if widget_key in st.session_state:
                    del st.session_state[widget_key]

                st.rerun()

        # st.markdown("---")

    # Add new query
    col, _ = st.columns([4, 10])
    col.text_input(
        "",
        key="new_query_label",
        placeholder="➕ Add search field (Enter field name and press Enter)",
        label_visibility="collapsed",
        on_change=add_query,
    )


def add_query():
    label = st.session_state.new_query_label.strip()

    if not label:
        return

    queries = ui.state.get_queries()
    if label in queries:
        return

    queries[label] = ""
    ui.state.set_queries(queries)

    # clear input safely
    st.session_state["new_query_label"] = ""


def display_search_results():
    layout = ui.state.get_layout()
    articles = layout.get_unassigned_articles()
    if not articles:
        st.write("No articles found for your search query.")
    for article in articles:
        title = article.title
        source = article.source
        published = f"{article.date_published_string} {article.time_published_string}"
        url = article.url if article.url else article.google_url
        if not article.url:
            missing_text_message = """Text for this article could not be obtained because we could not decode the Google RSS link.
            Sometimes this can happen if we've recently tried to decode too many Google RSS links in a short period of time.
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
            selectbox_key = f"selectbox_add_unassigned_article_to_section_{article.id}"
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
                key=f"fully_delete_unassigned_article_{article.id}",
                on_click=layout.delete_unassigned_article,
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
