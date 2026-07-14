import streamlit as st
import ui.state
from models.layout import Layout
from models.section import Section
from streamlit_sortables import sort_items
from utils.config import load_default_section_names


def initialize_layout():
    section_names = load_default_section_names()
    ui.state.set_layout(Layout(section_names=section_names))


def show_layout_section():
    st.header("Organize Report")
    st.subheader("Manage Report Sections")
    show_manage_sections()
    st.subheader("Manage Articles")
    show_section_tabs()


def show_manage_sections():
    layout = ui.state.get_layout()
    # Show each section in order. When a user moves a section, update the Layout and the UI.
    section_names = [s.name for s in layout.get_ordered_sections()]

    reordered_names = sort_items(section_names, direction="vertical")
    if (len(section_names) == len(reordered_names)) and (section_names != reordered_names):
        old_position, new_position = find_move(section_names, reordered_names)
        layout.reorder_section(old_position, new_position)
        st.rerun()

    if "section_add_error" in st.session_state:
        st.error(st.session_state["section_add_error"])
        del st.session_state["section_add_error"]

    col, _ = st.columns([4, 10])
    col.text_input(
        "",
        key="new_section_text_input",
        placeholder="➕ Add new section (Enter section name and press Enter)",
        label_visibility="collapsed",
        on_change=add_section_from_text_input,
        kwargs={"widget_key": "new_section_text_input"},
    )


def add_section_from_text_input(widget_key):
    layout = ui.state.get_layout()
    section_name = st.session_state[widget_key]
    try:
        layout.add_section(section_name=section_name)
        st.session_state[widget_key] = ""  # Clear the input
    except ValueError as e:
        st.session_state["section_add_error"] = str(e)


def set_delete_section_pending(section_id: str):
    st.session_state["delete_section_pending"] = section_id


@st.dialog("Delete Section?")
def show_delete_section_confirmation():
    layout = ui.state.get_layout()
    section_id = st.session_state["delete_section_pending"]

    if section_id not in layout.sections:
        st.error("Section not found.")
        if st.button("Close"):
            del st.session_state["delete_section_pending"]
            st.rerun()
        return

    section = layout.sections[section_id]
    article_count = len(section.articles)

    st.write(f"Are you sure you want to delete the section **{section.name}**?")
    if article_count > 0:
        st.write(
            f"This section contains **{article_count}** article(s) that will be moved to the unassigned list."
        )
    else:
        st.write("This section is empty.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Confirm Delete", type="primary", use_container_width=True):
            layout.delete_section(section_id)
            del st.session_state["delete_section_pending"]
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            del st.session_state["delete_section_pending"]
            st.rerun()


def show_section_tabs():
    layout = ui.state.get_layout()
    sections = layout.get_ordered_sections()
    with st.container(border=True):
        tabs = st.tabs([s.name for s in sections], on_change="rerun")
        for tab, section in zip(tabs, sections):
            with tab:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.button(
                        "**Delete Section** (This will move all articles in the section to the bottom of the query results list.)",
                        key=f"delete_section_button_{section.id}",
                        on_click=set_delete_section_pending,
                        kwargs={"section_id": section.id},
                        use_container_width=True,
                    )
                if section.has_articles():
                    show_articles(section)

    if "delete_section_pending" in st.session_state:
        show_delete_section_confirmation()


def show_articles(section: Section):
    layout = ui.state.get_layout()
    section_id = section.id
    for i, article_id in enumerate(section.articles):
        article = layout.articles[article_id]
        c1, c2, c3, c4 = st.columns([0.03, 0.03, 0.92, 0.03])
        if i > 0:
            c1.button(
                "⬆",
                key=f"up_{article_id}",
                use_container_width=True,
                type="tertiary",
                help="Move up within section.",
                on_click=section.move_article_up,
                kwargs={"article_position": i},
            )
        if i < len(section.articles) - 1:
            c2.button(
                "⬇",
                key=f"down_{article_id}",
                use_container_width=True,
                type="tertiary",
                help="Move down within section.",
                on_click=section.move_article_down,
                kwargs={"article_position": i},
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


def find_move(original, modified):
    """
    For a list with one element moved to a new position, returns the indexes of the old and new positions.
    Returns:
        (old_position, new_position).
    """
    start = next((i for i, (a, b) in enumerate(zip(original, modified)) if a != b), None)

    if start is None:
        ValueError("Lists are identical.")  # no move

    end = (
        len(original)
        - 1
        - next(i for i, (a, b) in enumerate(zip(reversed(original), reversed(modified))) if a != b)
    )

    # Moved right
    if original[start] == modified[end]:
        return start, end

    # Moved left
    if original[end] == modified[start]:
        return end, start

    raise ValueError("Lists are not related by a single move")
