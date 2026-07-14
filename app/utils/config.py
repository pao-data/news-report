import tomllib

import yaml

from utils.paths import BASE_DIR

DEFAULT_SECTION_NAMES = [
    "Recommended Top Stories",
    "USARPAC Lethality",
    "Army Priorities",
    "China & North Asia",
    "Southeast Asia",
    "Other News",
]

def load_config():
    config_path = BASE_DIR / "config.toml"
    with open(config_path, "rb") as f:
        return tomllib.load(f)
    
def load_default_queries():
    yaml_path = BASE_DIR / "app/assets/default_search_booleans.yaml"
    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)

def load_default_section_names() -> list[str]:
    config = load_config()
    section_names = config.get("defaults", {}).get("section_names")
    if not isinstance(section_names, list):
        return DEFAULT_SECTION_NAMES.copy()

    cleaned_names = []
    for name in section_names:
        if not isinstance(name, str):
            continue
        trimmed = name.strip()
        if not trimmed:
            continue
        cleaned_names.append(trimmed)

    if not cleaned_names:
        return DEFAULT_SECTION_NAMES.copy()

    return cleaned_names