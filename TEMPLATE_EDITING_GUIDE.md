# Guide: Editing the Report Template

This guide explains how to safely edit the Word document template used to generate news reports.

## Location

The default template is located at:
- `app/assets/default_template.docx`

## What You Can Edit

### ✅ Safe to Edit

**1. Font Formatting**
- Change font family (e.g., Arial, Times New Roman, Calibri)
- Change font sizes
- Change font colors
- Apply bold, italic, or underline

**2. Paragraph Formatting**
- Change line spacing (single, 1.5, double)
- Change paragraph spacing (before/after)
- Change alignment (left, center, right, justified)
- Change indentation

**3. Page Layout**
- Change margins (top, bottom, left, right)
- Change page size (Letter, A4, etc.)
- Change page orientation (portrait/landscape)
- Add headers and footers (but see warnings below)

**4. Colors and Styles**
- Change background colors
- Change border styles
- Change table formatting (if you add tables around content)

**5. Static Text**
- Add your organization's name or logo
- Add introductory text or instructions
- Add footer text (e.g., "Confidential", disclaimers)

## What You Must NOT Edit

### ❌ DO NOT Change These

**1. Template Variables (Text in Double Curly Braces)**

DO NOT modify or delete any text that looks like this:
- `{{ report_date.month }}`
- `{{ report_date.day }}`
- `{{ report_date.year }}`
- `{{ section.name }}`
- `{{ article.title_with_link }}`
- `{{ article.source }}`
- `{{ article.date }}`
- `{{ article.summary }}`
- `{{ article.full_text }}`

These are placeholders that the app fills in with actual data. If you change or delete them, the report will not generate correctly.

**2. Loop Statements (Text in Curly Braces with Percent Signs)**

DO NOT modify or delete any text that looks like this:
- `{% for section in sections %}`
- `{% for article in section.articles %}`
- `{% endfor %}`

These control how the app repeats content for multiple sections and articles. Changing them will break the report.

**3. The "FULL ARTICLES" Text**

There must be exactly one paragraph with the text `FULL ARTICLES` (in all caps, exactly as shown). This divider tells the app where the summary section ends and the full articles section begins. The navigation links depend on this.

**4. Navigation Link Text**

Keep these exact phrases unchanged:
- "Full Articles" (in the summary section)
- "Back to Top" (in the summary section)
- "Back to Summaries" (in the full articles section)

The app automatically converts these into clickable links. If you change the wording, the links won't work.

## How to Edit the Template

### Step 1: Make a Backup
Before editing, make a copy of the original template file and save it somewhere safe.

### Step 2: Open in Microsoft Word
Open the template file (`default_template.docx`) in Microsoft Word.

### Step 3: Make Your Changes
Apply your formatting changes to the parts of the document that are safe to edit (see "What You Can Edit" above).

**Example:** To change the font for article titles:
1. Find the line with `{{ article.title_with_link }}`
2. Select that entire line
3. Change the font, size, or color using Word's formatting tools
4. DO NOT change the text `{{ article.title_with_link }}` itself
5. **Make sure you edit the _entire line_ at once** – editing just part of the line can cause issues.

### Step 4: Save the File
Save the file with the same name (`default_template.docx`) in the same location.

### Step 5: Test the Template
1. Run the app
2. Generate a report
3. Check that all sections, articles, and navigation links work correctly
4. If something breaks, restore your backup and try again

## Using a Custom Template

If you want to use a completely different template without replacing the default:

1. Create your custom template based on the default one
2. In the app, go to the "Report Generation" section
3. Expand "Advanced: Upload custom template .docx file"
4. Upload your custom template
5. Generate the report

The app will use your uploaded template instead of the default one.

## Common Mistakes to Avoid

❌ **Deleting template variables** - This will cause missing data in your report
❌ **Changing the `FULL ARTICLES` text** - This will break navigation links
❌ **Adding text inside `{% for %}` loops** - This will repeat for every item
❌ **Changing navigation link phrases** - Links won't work
❌ **Removing the `{% endfor %}` statements** - The report won't generate

## Getting Help

If your template isn't working:
1. Restore the original template from your backup
2. Make smaller, incremental changes
3. Test after each change to identify what caused the problem
4. Check that all template variables and loop statements are intact

## Template Structure Overview

The template has this basic structure:

```
[Your custom header/title]

Date: {{ report_date.month }} {{ report_date.day }}, {{ report_date.year }}

[Loop through each section]
  Section Name: {{ section.name }}
  
  [Loop through each article in section]
    {{ article.title_with_link }}
    Source: {{ article.source }}
    Date: {{ article.date }}
    Summary: {{ article.summary }}
    [Navigation: Full Articles | Back to Top]
  [End article loop]
[End section loop]

FULL ARTICLES

[Loop through each section again]
  Section Name: {{ section.name }}
  
  [Loop through each article in section]
    {{ article.title_with_link }}
    Source: {{ article.source }}
    Date: {{ article.date }}
    Full Text: {{ article.full_text }}
    [Navigation: Back to Summaries]
  [End article loop]
[End section loop]
```

You can format any of this content, but don't change the variable names or structure.
