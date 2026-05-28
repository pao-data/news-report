from docxtpl import DocxTemplate
from io import BytesIO

def generate_doc_context(articles):
    context = {
        "report_date": {
            "day": 20,
            "month": "October",
            "year": 2026,
        },
        "sections": articles,
        # "sections": [
        #     {
        #         "name": "first section",
        #         "text": "the first text for this section",
        #         "full_text": "the second text for this section. This is longer!",
        #     },
        #     {
        #         "name": "second section",
        #         "text": "the first text for the second section!",
        #         "full_text": "the second text for the second section. This is longer than the first text was!\nThere was a new line character!",
        #     },
        # ]
    }
    return context

def generate_document(template, context):
    """
    template:    Path or file-like. Template word doc to use for report document generation.
    context:     Dict. The data used to fill in the template.
    """
    doc = DocxTemplate(template)
    doc.render(context)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer

if __name__ == "__main__":
    articles = []
    template_path = "basic_template.docx"
    context = generate_doc_context(articles)
    buffer = generate_document(template_path, context)
    with open("output_document.docx", "wb") as f:
        f.write(buffer.getvalue())
