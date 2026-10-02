import sys
from pathlib import Path


def ensure_app_on_path() -> None:
    app_dir = Path(__file__).resolve().parents[1] / "app"
    app_dir_str = str(app_dir)
    if app_dir_str not in sys.path:
        sys.path.insert(0, app_dir_str)
