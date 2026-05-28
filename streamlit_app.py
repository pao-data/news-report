from datetime import datetime
import logging

import streamlit as st

import document
import search

# TODO have the search terms Taylor gave me already in there
# TODO handle paywall issue
# TODO implement article selection
# TODO display articles on webpage (related to article selection)
# TODO allow number of articles to be set (currently defaulting to 5)
# TODO get date of story
# TODO generate downloadable report (if downloadable is possible, otherwise they may just have to copy/paste)

logging.basicConfig(
        filename=f"logs/main_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
        level=logging.INFO)

logger = logging.getLogger(__name__)

def display_articles(articles):
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
        st.checkbox(
            f"***{title}***",
            key=f"article_{i}",
        )
        st.write(f"Date:\t{date}")
        st.write(f"Link:\t{url}")
        st.write(f"{text_preview}")

# def display_articles(articles):
#     for i, article in enumerate(articles, start=1):
#         st.checkbox(
#             f'{article["title"]} ({article["url"]})',
#             key=f"article_{i}",
#         )
        
#         st.subheader(f"{i}. {article.get('title', '(no title)')}")
#         st.write(f"url:\t{article.get('url', '--no url found--')}")
#         if "text" in article and article["text"]:
#             st.write("Text:")
#             st.write(article["text"][:300])
#             st.write("...")
#             st.write(article["text"][-300:])
#         else:
#             st.info("No text extracted.")


st.title("Morning Report")

query = st.text_input("Search query:")

if st.button("Search!"):
    logger.info(f"User searched: {query}")
    with st.spinner("Searching for news articles..."):
        articles = search.get_news(query, 5)
    display_articles(articles)