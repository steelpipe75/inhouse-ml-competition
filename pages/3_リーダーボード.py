import streamlit as st

from custom_settings import (
    LEADERBOARD_SORT_ASCENDING,
    read_leaderboard,
    filter_leaderboard,
)

# 認証チェック
if not st.session_state.get("authenticated", False):
    st.error("Home画面で合言葉を入力してください。")
    st.stop()


def show_leaderboard() -> None:
    st.title("リーダーボード")
    leaderboard = read_leaderboard()
    if not leaderboard.empty:
        leaderboard = leaderboard.sort_values(
            "public_score", ascending=LEADERBOARD_SORT_ASCENDING
        )
        df = filter_leaderboard(leaderboard)
        st.dataframe(df)
    else:
        st.info("まだ投稿がありません。")


show_leaderboard()
