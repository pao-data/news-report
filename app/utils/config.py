import streamlit as st
import tomllib

from utils.paths import BASE_DIR

@st.cache_data # TODO does cache data make it so the function doesn't update results if the config.toml content changes??
def load_config():
    config_path = BASE_DIR / "config.toml"
    with open(config_path, "rb") as f:
        return tomllib.load(f)