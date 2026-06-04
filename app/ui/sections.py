import streamlit as st
from streamlit_sortables import sort_items

from models.article import Article
from models.section import Section

def show_sections():
    section_names = ["Recommended Top Stories", "USARPAC Lethality", "Army Priorities", "China & North Asia", "Southeast Asia", "Other News"]
    with st.container(border=True):
        tabs = st.tabs(section_names)

    if not st.session_state["sections"]:
        sections = []
        for section_name in section_names:
            sections.append(
                Section(name=section_name, articles=[])
            )
        # temporary hack; overwrite first section
        if st.session_state["articles"]:
            sections[0] = Section(
                name=section_names[0],
                articles=st.session_state["articles"][:3]
            )
        st.session_state["sections"] = sections

    with tabs[0]:
        if st.session_state["articles"]:
            show_articles(st.session_state["sections"][0])



def show_articles(section: Section):
    _, c_move, _, c_del = st.columns([0.01, 0.08, 0.87, 0.04], vertical_alignment="bottom")
    c_move.write("*Reorder*")
    c_del.write("*Delete*")
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
        c4.button(" ", key=f"delete_{i}", icon=":material/delete:", type="tertiary")
        
        # with c4.popover("change section", key=f"move_{i}", type="secondary"):
        #     st.write("hi")


    # if "sections" not in st.session_state:
    #     st.session_state.sections = [
    #         "Introduction",
    #         "Methods",
    #         "Results",
    #     ]

    # for i, section in enumerate(st.session_state.sections):
    #     c1, c2, c3, c4 = st.columns([4, 1, 1, 1])

    #     c1.write(section)

    #     # Move up
    #     if c2.button("↑", key=f"up_{i}") and i > 0:
    #         sections = st.session_state.sections
    #         sections[i - 1], sections[i] = sections[i], sections[i - 1]
    #         st.rerun()

    #     # Move down
    #     if c3.button("↓", key=f"down_{i}") and i < len(st.session_state.sections) - 1:
    #         sections = st.session_state.sections
    #         sections[i + 1], sections[i] = sections[i], sections[i + 1]
    #         st.rerun()

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