import streamlit as st

pg = st.navigation([st.Page("pages/home.py"), st.Page("pages/convert_html.py")])
pg.run()
