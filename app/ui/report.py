from io import BytesIO

import core.report
import streamlit as st
import ui.state
from utils.config import load_config
from utils.paths import BASE_DIR


def reset_template_doc():
    ui.state.set_user_provided_template(None)


def get_template():
    user_template = ui.state.get_user_provided_template()
    if user_template:
        return user_template
    else:
        config = load_config()
        default_template_path = BASE_DIR / config["paths"]["default_template_file"]
        return default_template_path


def generate_report_for_download():
    layout = ui.state.get_layout()
    template = get_template()
    buffer = core.report.generate_document(layout, template)

    st.download_button(
        label="Download DOCX",
        data=buffer,
        file_name="report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


def show_report_section():
    st.subheader("Report Generation")
    with st.expander("Advanced: Upload custom template .docx file for report generation."):
        st.write(
            "Warning! Uploading a template report in the wrong format can cause the report to generate incorrectly. "
            "Please don't use this option unless you know what you're doing."
        )
        template_file_upload = st.file_uploader("Upload a DOCX template", type=["docx"])
        if template_file_upload:
            user_provided_template = BytesIO(template_file_upload.read())
            ui.state.set_user_provided_template(user_provided_template)
        else:
            # If user removes an uploaded template document, use the default template.
            reset_template_doc()

    if st.button("Generate Report"):
        generate_report_for_download()
