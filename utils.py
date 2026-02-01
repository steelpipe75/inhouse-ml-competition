import streamlit as st
import hashlib
import hmac
from PIL import Image

from config import (
    PROTECT_ALL_PAGES,
    PAGE_TITLE,
    PAGE_ICON,
    AUTH,
)


def show_register_ground_truth_message() -> None:
    """
    ground_truthの登録を促すメッセージを表示する。
    db_pathが指定された場合、新規作成された旨も表示する。
    """

    st.info(
        "正解データが登録されていません。`ground_truth` を登録してください。\n\n"
        "登録するには、プロジェクトのルートディレクトリで以下のコマンドを実行してください：\n\n"
        "```\n"
        "poetry run python scripts/register_ground_truth.py\n"
        "```"
    )


def page_config() -> None:
    favicon = Image.open("favicon.ico")
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=favicon,
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

    # st.session_stateに"authenticated"がない場合はFalseをセット
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # APP_PASSWORD_HASH が設定されているかチェックし、設定されていない場合は認証をスキップ
    try:
        _ = st.secrets["APP_PASSWORD_HASH"]
        password_hash_exists = True
    except (KeyError, FileNotFoundError):
        password_hash_exists = False

    if AUTH:
        with st.sidebar:
            if not st.user.is_logged_in:
                if st.button("ログイン", icon=":material/login:"):
                    st.login()
            else:
                if st.button("ログアウトする", icon=":material/logout:"):
                    st.logout()
                    st.rerun()

                st.caption(
                    f":material/account_circle: user : {st.user.name}  \n:material/mail: email : {st.user.email}"
                )
    else:
        if password_hash_exists:
            with st.sidebar:
                if st.session_state.authenticated:
                    st.write(":material/lock_open:")
                else:
                    st.write(":material/lock:")

    # このページが保護対象かどうかを判断
    if not PROTECT_ALL_PAGES and not always_protect:
        return  # 保護対象外なので何もしない

    # --- 以下、保護対象ページの場合のロジック ---
    if AUTH:
        if not st.user.is_logged_in:
            st.subheader(
                ":material/lock: このページの内容にアクセスするにはログインしてください"
            )
            if st.button("ログイン", icon=":material/login:"):
                st.login()
            st.stop()
    else:
        if not password_hash_exists:
            st.session_state.authenticated = True
            return

        # 認証済みの場合は、ここで処理を終了
        if st.session_state.authenticated:
            return

        # --- 以下、未認証の場合の処理 ---
        st.subheader(
            ":material/lock: このページの内容にアクセスするには合言葉を入力してください"
        )
        password = st.text_input("合言葉", type="password", key="password_input")

        if st.button("ロック解除", icon=":material/lock_open:"):
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


