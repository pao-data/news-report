import streamlit as st
import tomllib

import yaml

from utils.paths import BASE_DIR

def load_config():
    config_path = BASE_DIR / "config.toml"
    with open(config_path, "rb") as f:
        return tomllib.load(f)
    
def load_default_queries():
    yaml_path = BASE_DIR / "app/assets/default_search_booleans.yaml"
    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)