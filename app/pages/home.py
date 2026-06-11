import logging
from datetime import datetime

import streamlit as st

from utils.paths import BASE_DIR
from ui.search import show_search_section
from ui.report import show_report_section
from ui.layout import show_layout_section, initalize_layout


logging.basicConfig(
        filename=BASE_DIR / f"logs/main_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
        level=logging.INFO)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    if "articles" not in st.session_state:
        st.session_state.articles = []
    if "sections" not in st.session_state:
        st.session_state.sections = []
    if "layout" not in st.session_state:
        initalize_layout()
    if "user_provided_template" not in st.session_state:
        st.session_state.user_provided_template = None
    if "show_search_results" not in st.session_state:
        st.session_state.show_search_results = False

    st.set_page_config(layout="wide")
    
    st.title("Morning Report")

    show_layout_section()
    show_search_section()
    show_report_section()
    
