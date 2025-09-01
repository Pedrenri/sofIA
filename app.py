import os
import streamlit as st
from dotenv import load_dotenv
from dev_interface import dev_mode
from wake_word_interface import listen_for_wake_word

# Load environment variables from .env
load_dotenv()

st.set_page_config(page_title="SofIA", layout="centered")

dev_mod_status = os.getenv("DEV_MODE", "False").lower() in ("true", "1", "yes")


if dev_mod_status:
    st.warning("🚧 Modo de Desenvolvimento Ativado")
    dev_mode()
else:
    listen_for_wake_word()
