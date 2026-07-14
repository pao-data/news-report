import core.extraction
import streamlit as st

st.write("Extract article text from html")

user_input = st.text_area(
    label="Insert raw HTML text", placeholder="Paste raw HTML text here", height="content"
)

extracted_text = core.extraction.extract_main_text(raw_html=user_input)  # , output_format="xml")
# extracted_text = json.loads(extracted_text)

if user_input:
    st.divider()
    st.text(extracted_text)
    # pretty_xml = minidom.parseString(extracted_text).toprettyxml(indent="  ")
    # st.text(pretty_xml)
    # for k, v in extracted_text.items():
    #     st.write(f"**{k}**")
    #     st.write(v)
