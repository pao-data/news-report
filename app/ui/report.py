import streamlit as st

from io import BytesIO

import core.report
from utils.config import load_config
from utils.paths import BASE_DIR

def reset_template_doc():
    st.session_state["user_provided_template"] = None

def get_template():
    if st.session_state["user_provided_template"]:
        return st.session_state["user_provided_template"]
    else:
        config = load_config()
        default_template_path = BASE_DIR / config["paths"]["default_template_file"]
        return default_template_path
    
def get_selected_articles():
    articles = st.session_state["articles"]
    selected_articles = []
    for article in articles:
        key = article.id
        is_checked = st.session_state[key]
        if is_checked:
            selected_articles.append(article)
    return selected_articles

def generate_report_for_download():
    articles = get_selected_articles()
    template = get_template()
    buffer = core.report.generate_document(articles, template)

    st.download_button(
        label="Download DOCX",
        data=buffer,
        file_name="report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

def show_report_section():
    st.markdown("### Report Generation")
    with st.expander("Advanced: Upload custom template .docx file for report generation."):
        st.write(
            "Warning! Uploading a template report in the wrong format can cause the report to generate incorrectly. "
            "Please don't use this option unless you know what you're doing."
        )
        template_file_upload = st.file_uploader(
            "Upload a DOCX template",
            type=["docx"]
        )
        if template_file_upload:
            user_provided_template = BytesIO(template_file_upload.read())
            st.session_state["user_provided_template"] = user_provided_template
        else:
            # If user removes an uploaded template document, use the default template.
            reset_template_doc()
        
    if st.button("Generate Report"):
        generate_report_for_download()