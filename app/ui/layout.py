import streamlit as st
from streamlit_sortables import sort_items

from models.article import Article
from models.section import Section
from models.layout import Layout

def initalize_layout():
    section_names = ["Recommended Top Stories", "USARPAC Lethality", "Army Priorities", "China & North Asia", "Southeast Asia", "Other News"]
    st.session_state.layout = Layout(section_names=section_names)
    st.rerun()
    
def show_layout_section():
    show_manage_sections()
    show_section_tabs()

def show_manage_sections():
    layout = st.session_state.layout
    # Show each section in order. When a user moves a section, update the Layout and the UI.
    sections = get_numbered_list(layout.get_ordered_section_names())
    reordered_sections = sort_items(sections, direction="vertical")
    if sections != reordered_sections:
        old_position, new_position = find_move(sections, reordered_sections)
        layout.reorder_section(old_position, new_position)
        st.rerun()

def show_section_tabs():
    layout = st.session_state.layout
    section_names = layout.get_ordered_section_names()
    with st.container(border=True):
        tabs = st.tabs(section_names)

    # with tabs[0]:
    #     if st.session_state["articles"]:
    #         show_articles(st.session_state["sections"][0])


# TODO show_articles will need to be passed the layout
def show_articles(section: Section):
    _, c_move, _, c_del = st.columns([0.01, 0.08, 0.87, 0.04], vertical_alignment="bottom")
    c_move.write("*Reorder within section*")
    c_del.write("*Remove from report*")
    for i, article in enumerate(section.articles):
        c1, c2, c3, c4 = st.columns([0.03, 0.03, 0.92, 0.03])
        if i > 0:
            c1.button(
                "⬆", key=f"up_{i}", use_container_width=True, type="tertiary",
                on_click=section.move_article_up, kwargs={"article_position": i}
            )
        if i < len(section.articles)-1:
            c2.button(
                "⬇", key=f"down_{i}", use_container_width=True, type="tertiary",
                on_click=section.move_article_down, kwargs={"article_position": i}
            )
        with c3:
            show_article_expander(article)
        c4.button(
            " ", key=f"delete_{i}", icon=":material/delete:", type="tertiary"
        ) # TODO on click layout.unassign_article(article_id, from_id)
        
        # with c4.popover("change section", key=f"move_{i}", type="secondary"):
        #     st.write("hi")

    # for i, section in enumerate(st.session_state.sections):
    #     c1, c2, c3, c4 = st.columns([4, 1, 1, 1])

    #     c1.write(section)

    #     # Delete
    #     if c4.button("❌", key=f"delete_{i}"):
    #         st.session_state.sections.pop(i)
    #         st.rerun()

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

    