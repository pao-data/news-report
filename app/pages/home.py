import logging
from datetime import datetime

import streamlit as st
import ui.state
from ui.layout import initialize_layout, show_layout_section
from ui.report import show_report_section
from ui.search import show_search_section
from utils.config import load_default_queries
from utils.paths import BASE_DIR

log_dir = BASE_DIR / "logs"
if log_dir.exists() and log_dir.is_dir():
    logging.basicConfig(
        filename=BASE_DIR / f"logs/main_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
        level=logging.INFO,
    )
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    ui.state.ensure_state_initialized(
        default_queries=load_default_queries(),
        initialize_layout_fn=initialize_layout,
    )

    st.set_page_config(layout="wide")

    st.title("Morning Report")

    show_search_section()
    show_layout_section()
    show_report_section()
