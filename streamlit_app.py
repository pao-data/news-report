from datetime import datetime
import logging

import streamlit as st

import search

logging.basicConfig(
        filename=f"logs/main_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
        level=logging.INFO)

logger = logging.getLogger(__name__)

def display_articles(articles):
    for i, article in enumerate(articles, start=1):
        st.subheader(f"{i}. {article.get('title', '(no title)')}")
        st.write(f"url:\t{article.get('url', '--no url found--')}")
        for text in ["clean_text", "raw_text"]:
            if text in article and article[text]:
                h = "Clean Text" if text=="clean_text" else "Raw Text"
                st.write(f"{h}:")
                st.write(article[text][:400])
                st.write("...")
                st.write(article[text][-100:])
            elif "error" in article:
                st.error(f"Fetch failed: {article['error']}")
            else:
                st.info("No text extracted.")

st.title("Morning Report")

query = st.text_input("Search query:")

if st.button("Search!"):
    logger.info(f"User searched: {query}")
    st.write(f"You searched for: {query}")
    articles = search.get_news(query, 5)
    display_articles(articles)