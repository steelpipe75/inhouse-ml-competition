from typing import List, Optional, Tuple
import pandas as pd
import streamlit as st
import hashlib
import hmac

from config import (
    PROTECT_ALL_PAGES,
    PAGE_TITLE,
    PAGE_ICON,
    AUTH,
)


def page_config() -> None:
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.logo(
        image="./logo.png",
        size="large",
        icon_image="./icon.png",
    )


def check_password(always_protect: bool = False) -> None:
    """
    合言葉をチェックし、認証されていなければパスワード入力を表示し、
    プログラムの実行を停止する。
    認証済みの場合は何もしない。
    `always_protect` が True のページ、または `config.py` の `PROTECT_ALL_PAGES` が
    True の場合に認証が実行される。
    """

    if AUTH:
        with st.sidebar:
            if not st.user.is_logged_in:
                if st.button("ログイン", icon=":material/login:"):
                    st.login()
            else:
                if st.button("ログアウトする", icon=":material/logout:"):
                    st.logout()
                    st.rerun()

                st.caption(f"user : {st.user.name}  \nemail : {st.user.email}")

    # このページが保護対象かどうかを判断
    if not PROTECT_ALL_PAGES and not always_protect:
        return  # 保護対象外なので何もしない

    # --- 以下、保護対象ページの場合のロジック ---
    if AUTH:
        if not st.user.is_logged_in:
            st.subheader("このページの内容にアクセスするにはログインしてください")
            if st.button("ログイン", icon=":material/login:"):
                st.login()
            st.stop()
    else:
        # st.session_stateに"authenticated"がない場合はFalseをセット
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False

        # APP_PASSWORD_HASH が設定されているかチェックし、設定されていない場合は認証をスキップ
        try:
            _ = st.secrets["APP_PASSWORD_HASH"]
            password_hash_exists = True
        except (KeyError, FileNotFoundError):
            password_hash_exists = False

        if not password_hash_exists:
            st.session_state.authenticated = True
            return

        # 認証済みの場合は、ここで処理を終了
        if st.session_state.authenticated:
            return

        # --- 以下、未認証の場合の処理 ---
        st.title(PAGE_TITLE)
        st.subheader("合言葉を入力してください")
        password = st.text_input("合言葉", type="password", key="password_input")

        if st.button("ログイン"):
            correct_password_hash = st.secrets["APP_PASSWORD_HASH"]

            # 入力された合言葉をハッシュ化
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            if hmac.compare_digest(password_hash, correct_password_hash):
                st.session_state.authenticated = True
                st.rerun()  # 認証後にページを再読み込み
            else:
                st.error("合言葉が違います。")

        # 認証が完了するまで、これ以降のコードは実行させない
        st.stop()

