import streamlit as st
import streamlit.components.v1 as components

from utils import check_password

# 認証チェック
check_password()


def playground() -> None:
    st.title("playground")

    components.iframe("https://steelpipe75.github.io/inhouse-ml-competition-playground-sample/")


playground()
