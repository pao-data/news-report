import streamlit as st
import logging

import core.search

logger = logging.getLogger(__name__)

def show_search_section():
    st.markdown("### Search Google News")
    query = st.text_input("Search query:")

    if st.button("Search!"):
        logger.info(f"User searched: {query}")
        st.session_state["show_search_results"] = False
        with st.spinner("Searching for news articles..."):
            articles = core.search.get_news(query, 5)
            st.session_state["articles"] = articles
            st.session_state["show_search_results"] = True

    if st.session_state["show_search_results"]:
        articles_with_checkbox_keys = display_search_results(st.session_state["articles"])
        st.session_state["articles"] = articles_with_checkbox_keys

def display_search_results(articles):
    if not articles:
        st.write("No articles found for your search query.")
    articles_with_checkbox_keys = []
    for i, article in enumerate(articles, start=1):
        title = article["title"]
        date = article["date"]
        url = article["url"]
        text = article["text"]
        if text is None:
            text_preview = "Text for this article could not be found. This article is possibly behind a paywall."
        elif len(text) <= 600:
            text_preview = text
        else:
            text_preview = text[:300] + "\n...\n" + text[-300:]
        checkbox_key = f"article_checkbox_{i}"
        st.checkbox(
            f"***{title}***",
            key=checkbox_key,
            value=True,
        )
        article["checkbox_key"] = checkbox_key
        articles_with_checkbox_keys.append(article)
        st.write(f"Date:\t{date}")
        st.write(f"Link:\t{url}")
        st.write(f"{text_preview}")
    return articles_with_checkbox_keys