import streamlit as st
from streamlit_sortables import sort_items

from models.section import Section
from models.layout import Layout
from utils.config import load_default_section_names
import ui.state

def initialize_layout():
    section_names = load_default_section_names()
    ui.state.set_layout(Layout(section_names=section_names))
    st.rerun()
    
def show_layout_section():
    st.header("Organize Report")
    st.subheader("Manage Report Sections")
    show_manage_sections()
    st.subheader("Manage Articles")
    show_section_tabs()

def show_manage_sections():
    layout = ui.state.get_layout()
    # Show each section in order. When a user moves a section, update the Layout and the UI.
    sections = get_numbered_list(
        [s.name for s in layout.get_ordered_sections()]
    )
    reordered_sections = sort_items(sections, direction="vertical")
    if sections != reordered_sections:
        old_position, new_position = find_move(sections, reordered_sections)
        layout.reorder_section(old_position, new_position)
        st.rerun()
    
    col, _ = st.columns([4, 10])
    col.text_input(
        "",
        key="new_section_text_input",
        placeholder="➕ Add new section (Enter section name and press Enter)",
        label_visibility="collapsed",
        on_change=add_section_from_text_input,
        kwargs={"widget_key": "new_section_text_input"}
    )

def add_section_from_text_input(widget_key):
    layout = ui.state.get_layout()
    layout.add_section(
        section_name=st.session_state[widget_key]
    )

def show_section_tabs():
    layout = ui.state.get_layout()
    sections = layout.get_ordered_sections()
    with st.container(border=True):
        tabs = st.tabs([s.name for s in sections], on_change="rerun")
        for tab, section in zip(tabs, sections):
            with tab:
                if section.has_articles():
                    show_articles(section)


def show_articles(section: Section):
    layout = ui.state.get_layout()
    section_id = section.id
    for i, article_id in enumerate(section.articles):
        article = layout.articles[article_id]
        c1, c2, c3, c4 = st.columns([0.03, 0.03, 0.92, 0.03])
        if i > 0:
            c1.button(
                "⬆", key=f"up_{article_id}", use_container_width=True, type="tertiary",
                help="Move up within section.",
                on_click=section.move_article_up, kwargs={"article_position": i}
            )
        if i < len(section.articles)-1:
            c2.button(
                "⬇", key=f"down_{article_id}", use_container_width=True, type="tertiary",
                help="Move down within section.",
                on_click=section.move_article_down, kwargs={"article_position": i}
            )
        with c3:
            show_article_expander(article)
        c4.button(
            " ",
            key=f"delete_article_{article_id}_section_{section_id}",
            icon=":material/delete:",
            type="tertiary",
            help="Remove from report. (Article will return to the bottom of the search results list.)",
            on_click=layout.unassign_article,
            kwargs={"article_id": article_id, "from_id": section_id},
        )

def show_article_expander(article):
    title = article.title
    source = article.source
    published = f"{article.date_published_string} {article.time_published_string}"
    url = article.url
    text = article.full_text
    preview_text = text[:50] if text else ""
    with st.expander(f"**{title}**"):
        st.write(f"Source:\t{source}")
        st.write(f"Published:\t{published}")
        st.write(f"Link:\t{url}")
        st.write(f"{preview_text}")



def get_numbered_list(raw_list, start_with_one=True):
    offset = 1 if start_with_one else 0
    return [
        f"({idx+offset})\t{itm}"
        for idx, itm
        in enumerate(raw_list)
    ]
    
def find_move(original, modified):
    """
    For a list with one element moved to a new position, returns the indexes of the old and new positions.
    Returns:
        (old_position, new_position).
    """
    start = next(
        (i for i, (a, b) in enumerate(zip(original, modified)) if a != b),
        None
    )

    if start is None:
        ValueError("Lists are identical.")  # no move

    end = len(original) - 1 - next(
        i for i, (a, b) in enumerate(zip(reversed(original), reversed(modified)))
        if a != b
    )

    # Moved right
    if original[start] == modified[end]:
        return start, end

    # Moved left
    if original[end] == modified[start]:
        return end, start

    raise ValueError("Lists are not related by a single move")

    