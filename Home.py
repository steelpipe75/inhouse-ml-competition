import streamlit as st
import os
from custom_settings import HOME_CONTENT_FILE
from utils import check_password

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)


def show_home_content():
    """ホーム画面のコンテンツを表示する"""
    if os.path.exists(HOME_CONTENT_FILE):
        with open(HOME_CONTENT_FILE, encoding="utf-8") as f:
            content = f.read()
        st.markdown(content)
    else:
        st.title("内輪向け機械学習コンペアプリ")
        st.write("サイドバーから、各ページに移動できます。")
        st.error(f"Home表示内容カスタマイズ用ファイル（{HOME_CONTENT_FILE}）が見つかりません)")


def main() -> None:
    """メイン関数"""
    check_password()
    show_home_content()


if __name__ == "__main__":
    main()
