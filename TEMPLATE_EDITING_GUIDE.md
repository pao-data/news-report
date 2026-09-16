# Guide: Editing the Report Template

This guide explains how to safely edit the Word document template used to generate news reports.


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

### Step 1: Download the Template from the App
1. Open the app and go to the "Report Generation" section
2. Expand the "📝 Template Customization" section
3. Click the **"⬇️ Download Original Template"** button
4. Save the file to your computer (e.g., Desktop or Documents folder)

### Step 2: Edit in Microsoft Word
1. Open the downloaded `default_template.docx` file in Microsoft Word
2. Make your formatting changes (see "What You Can Edit" above)
3. **Important:** Do NOT change any template variables (text in `{{ }}` or `{% %}`)
4. Save your changes

**Example:** To change the font for article titles:
1. Find the line with `{{ article.title_with_link }}`
2. Select that entire line
3. Change the font, size, or color using Word's formatting tools
4. DO NOT change the text `{{ article.title_with_link }}` itself
5. **Make sure you edit the _entire line_ at once** – editing just part of the line can cause issues.
6. Save the file

### Step 3: Upload Your Edited Template
1. Go back to the app's "Report Generation" section
2. In the "📝 Template Customization" section, find **"Step 3: Upload Your Edited Template"**
3. Select your edited template from the file picker dialog
4. The app will confirm with a success message
5. Your custom template is now active for this session

### Step 4: Test Your Template
1. Click "Generate Report" to create a report with your custom template
2. Download and open the report
3. Check that all sections, articles, and navigation links work correctly
4. If something looks wrong, remove the uploaded file and re-upload a corrected version

## Session-Based vs. Permanent Changes

### Session-Based (What You Can Do)

Custom templates uploaded through the app are **session-based**:
- ✅ Work for the current session
- ✅ Can be changed anytime during the session
- ⚠️ Resets if you refresh the page or close the browser
- 💡 Tip: Save your edited template locally for easy re-upload

### Permanent Changes (Requires Developer)

If you need a permanent template change that persists across app restarts:
- Contact the developer/maintainer
- They can replace the default template in the codebase
- This requires git access and cannot be done through the app
- See README.md in the GitHub repository for developer instructions

## Common Mistakes to Avoid

❌ **Deleting template variables** - This will cause missing data in your report
❌ **Changing the `FULL ARTICLES` text** - This will break navigation links
❌ **Adding text inside `{% for %}` loops** - This will repeat for every item
❌ **Changing navigation link phrases** - Links won't work
❌ **Removing the `{% endfor %}` statements** - The report won't generate

## Getting Help

If your template isn't working:
1. Download the original template again from the app
2. Make smaller, incremental changes
3. Test after each change to identify what caused the problem
4. Check that all template variables and loop statements are intact
5. Remove the uploaded template and try again with a fresh edit

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
