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
