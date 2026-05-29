import logging
from datetime import datetime

import streamlit as st

from utils.paths import BASE_DIR
from ui.search import show_search_section
from ui.report import show_report_section

# TODO have the search terms Taylor gave me already in there
# TODO see how Taylor feels about the Access Denied from bot detection
# TODO allow number of articles to be set (currently defaulting to 5)
# TODO see if Taylor wants to sort the articles or prioritize them somehow
# TODO see how Taylor feels about potential cases where we can't decode the Google RSS url
# TODO (nice to have) create a feature that allowes users to add html text (to add text to an article)
# TODO (nice to have) create a feature that allowes users to add a url (to create a new article) – and add article to a section
# TODO (nice to have) see how Taylor feels about the section headers having their formatting stripped
# TODO (nice to have) add filter by date? 
# TODO (nice to have) recommended top stories


logging.basicConfig(
        filename=BASE_DIR / f"logs/main_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
        level=logging.INFO)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    if "articles" not in st.session_state:
        st.session_state["articles"] = []
    if "user_provided_template" not in st.session_state:
        st.session_state["user_provided_template"] = None
    if "show_search_results" not in st.session_state:
        st.session_state["show_search_results"] = False

    st.title("Morning Report")

    show_search_section()
    show_report_section()
    
