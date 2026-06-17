import streamlit as st
import tomllib

from utils.paths import BASE_DIR

def load_config():
    config_path = BASE_DIR / "config.toml"
    with open(config_path, "rb") as f:
        return tomllib.load(f)