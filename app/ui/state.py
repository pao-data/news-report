from collections.abc import Callable
from typing import Any

import streamlit as st

# Session state keys
QUERIES = "queries"
LAYOUT = "layout"
SHOW_SEARCH_RESULTS = "show_search_results"
USER_PROVIDED_TEMPLATE = "user_provided_template"
SECTIONS_LEGACY = "sections"


def ensure_state_initialized(
    *,
    default_queries: dict[str, str],
    initialize_layout_fn: Callable[[], None],
) -> None:
    if QUERIES not in st.session_state:
        st.session_state[QUERIES] = default_queries
    # Kept for compatibility with existing app startup behavior.
    if SECTIONS_LEGACY not in st.session_state:
        st.session_state[SECTIONS_LEGACY] = []
    if LAYOUT not in st.session_state:
        initialize_layout_fn()
    if USER_PROVIDED_TEMPLATE not in st.session_state:
        st.session_state[USER_PROVIDED_TEMPLATE] = None
    if SHOW_SEARCH_RESULTS not in st.session_state:
        st.session_state[SHOW_SEARCH_RESULTS] = False


def get_layout() -> Any:
    return st.session_state[LAYOUT]


def set_layout(layout: Any) -> None:
    st.session_state[LAYOUT] = layout


def get_queries() -> dict[str, str]:
    return st.session_state[QUERIES]


def set_queries(queries: dict[str, str]) -> None:
    st.session_state[QUERIES] = queries


def get_show_search_results() -> bool:
    return st.session_state[SHOW_SEARCH_RESULTS]


def set_show_search_results(value: bool) -> None:
    st.session_state[SHOW_SEARCH_RESULTS] = value


def get_user_provided_template() -> Any:
    return st.session_state[USER_PROVIDED_TEMPLATE]


def set_user_provided_template(template: Any) -> None:
    st.session_state[USER_PROVIDED_TEMPLATE] = template
