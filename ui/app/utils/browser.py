
import streamlit as st
from streamlit.components.v1 import html as st_html


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_to_local_storage(key: str, value: str) -> None:
    """Saves a value to the local storage of the browser.

    Args:
        key (str): The key under which the value will be stored.
        value (str): The value to be stored.
    """

    logger.info(f"Saving to local storage: {key} = {value}")


    st_html(
        f"""
        <script>
            console.log("Saving to local storage: {key} = {value}");
            localStorage.setItem("{key}", JSON.stringify("{value}"));
        </script>
        """,
        height=0,
    )

