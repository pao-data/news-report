# News Report App

Streamlit app for Morning News Report generation.

## Run locally

1. Create and activate a virtual environment:

   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install requirements:

   ```
   pip install -r requirements.txt
   ```

3. Start the app:

   ```
   streamlit run app/streamlit_app.py
   ```

4. The app can be viewed in your browser at `http://localhost:8501`. (You may have to change the port to reflect the port Streamlit runs the app on. It is usually 8501 but may change.)

## Development

The VS Code settings and recommended extensions should allow you to:
- automatically apply linting and formatting on save
- run unit tests using VS Code/Cursor's Test Explorer tool. 

The following CLI commands work as a fallback if your VS Code/Cursor is not configured correctly.

- Run tests:

  ```
  python -m unittest discover -s tests -v
  ```

- Lint and format with Ruff:

  ```
  ruff check .
  ruff format .
  ```

## Template Management

### For Users: Temporary Template Customization

Users can customize report templates for their session:

1. In the app, expand "📝 Template Customization"
2. Download the original template
3. Edit in Microsoft Word (see `TEMPLATE_EDITING_GUIDE.md`)
4. Upload the edited template back to the app
5. Custom template will be used for the remainder of the session

**Note:** Custom templates are session-based and reset when the app restarts.

### For Developers: Permanently Updating the Default Template

If users need a permanent template change (not just for one session), follow these steps:

1. **Get the edited template from the user**
   - Have them follow the customization steps above
   - Download their edited template from their local machine

2. **Test locally**
   ```bash
   # Replace the default template
   cp /path/to/user-edited-template.docx app/assets/default_template.docx
   
   # Start the app
   streamlit run app/streamlit_app.py
   
   # Generate a test report and verify all sections/links work
   ```

3. **Commit and deploy**
   ```bash
   git add app/assets/default_template.docx
   git commit -m "Update default report template"
   git push origin main
   ```

4. **Streamlit Cloud will automatically redeploy** with the new default template

### Why This Can't Be Done Through the App

Streamlit Cloud runs on a **read-only filesystem**. The app cannot write files that persist across restarts or deployments. Any files the app writes to disk are lost when:

- The app restarts
- The app is redeployed  
- The server is updated

To make permanent changes, files must be committed to the git repository, which requires developer access and cannot be done through the app UI. This is a security feature and deployment best practice for cloud applications.
