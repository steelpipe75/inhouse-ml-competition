import streamlit as st
import os
import hashlib
import hmac
from custom_settings import HOME_CONTENT_FILE


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
    # st.session_stateに"authenticated"がない場合はFalseをセット
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # 認証されていない場合は、パスワード入力を求める
    if not st.session_state.authenticated:
        st.title("内輪向け機械学習コンペアプリ")
        st.subheader("合言葉を入力してください")
        password = st.text_input("合言葉", type="password")

        if st.button("ログイン"):
            try:
                correct_password_hash = st.secrets["APP_PASSWORD_HASH"]
            except (KeyError, FileNotFoundError):
                st.error("合言葉のハッシュが設定されていません。管理者にお問い合わせください。")
                st.stop()

            # 入力された合言葉をハッシュ化
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            if hmac.compare_digest(password_hash, correct_password_hash):
                st.session_state.authenticated = True
                st.rerun()  # 認証後にページを再読み込み
            else:
                st.error("合言葉が違います。")
    else:
        # 認証済みの場合は、通常のコンテンツを表示
        show_home_content()


if __name__ == "__main__":
    main()
