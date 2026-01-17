import streamlit as st
import os

from custom_settings import DATA_DIR, PROBLEM_FILE
from utils import page_config, check_password

page_config()

# 認証チェック
check_password()


def show_overview_and_data() -> None:
    st.title("概要・データ")

    # 問題説明
    st.header("問題説明")
    if os.path.exists(PROBLEM_FILE):
        with open(PROBLEM_FILE, "r", encoding="utf-8") as f:
            problem_md = f.read()
        st.markdown(problem_md)
    else:
        st.error(f"問題説明ファイル（{PROBLEM_FILE}）が見つかりません。")

    # データダウンロード
    st.header("データダウンロード")
    if os.path.exists(DATA_DIR):
        for filename in os.listdir(DATA_DIR):
            filepath = os.path.join(DATA_DIR, filename)
            if os.path.isfile(filepath):
                with open(filepath, "rb") as f:
                    st.download_button(
                        f"{filename} をダウンロード", f, file_name=filename
                    )
    else:
        st.error("データフォルダが見つかりません。")


show_overview_and_data()
