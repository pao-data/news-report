import tomllib
import yaml
from utils.paths import BASE_DIR

DEFAULT_SECTION_NAMES = [
    "Recommended Top Stories",
    "USARPAC Lethality",
    "Army Priorities",
    "China & North Asia",
    "Southeast Asia",
    "Oceania & India",
    "Hawaii & South Pacific",
    "Across the Services",
    "Other News",
    "Commentary",
]


def normalize_section_name(name: str) -> str:
    """Return the normalized uniqueness key for a section name (trim + casefold)."""
    return name.strip().casefold()


def validate_section_name(name: str) -> str:
    """Validate and return the canonical display form of a section name (trimmed).

    Raises:
        ValueError: If the name is empty after trimming.
    """
    trimmed = name.strip()
    if not trimmed:
        raise ValueError("Section name cannot be empty or whitespace-only.")
    return trimmed


def check_duplicate_section_names(names: list[str]) -> None:
    """Check for duplicate section names using case-insensitive comparison.

    Args:
        names: List of section names to check.

    Raises:
        ValueError: If duplicate section names are found (after trim + casefold).
    """
    seen = {}
    for name in names:
        normalized = normalize_section_name(name)
        if normalized in seen:
            raise ValueError(
                f"Duplicate section name detected: '{seen[normalized]}' and '{name}' "
                f"are considered identical (case-insensitive after trimming)."
            )
        seen[normalized] = name


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

    check_duplicate_section_names(cleaned_names)
    return cleaned_names
