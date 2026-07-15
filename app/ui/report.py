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
        user_template.seek(0)
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

    with st.expander("📝 Template Customization"):
        st.write(
            "Customize the report template by downloading, editing in Microsoft Word, "
            "and uploading it back. Your custom template will be used for this session."
        )

        st.write("**Step 1: Download the Template**")
        config = load_config()
        default_template_path = BASE_DIR / config["paths"]["default_template_file"]
        with open(default_template_path, "rb") as f:
            st.download_button(
                label="⬇️ Download Original Template",
                data=f.read(),
                file_name="default_template.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                help="Download the template to edit in Microsoft Word",
            )

        st.write("**Step 2: Edit in Microsoft Word**")
        guide_path = BASE_DIR / "TEMPLATE_EDITING_GUIDE.pdf"
        with open(guide_path, "rb") as f:
            st.download_button(
                label="📚 Download Editing Instructions (PDF)",
                data=f.read(),
                file_name="TEMPLATE_EDITING_GUIDE.pdf",
                mime="application/pdf",
                help="Download detailed instructions for editing the template",
            )

        st.write("**Step 3: Upload Your Edited Template**")
        st.warning(
            "⚠️ Custom templates are session-based and reset when the app restarts. "
            "Contact a developer if you want to permanently change the default template."
        )

        template_file_upload = st.file_uploader(
            "Upload your edited template",
            type=["docx"],
            help="Upload a .docx file to use for this session",
        )
        if template_file_upload:
            user_provided_template = BytesIO(template_file_upload.read())
            ui.state.set_user_provided_template(user_provided_template)
            st.success("✅ Custom template uploaded! It will be used for this session.")
        else:
            # If user removes an uploaded template document, use the default template.
            reset_template_doc()

    if st.button("Generate Report"):
        generate_report_for_download()
