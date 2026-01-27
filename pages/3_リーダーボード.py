import streamlit as st

from custom_settings import (
    LEADERBOARD_SORT_ASCENDING,
    read_leaderboard,
    filter_leaderboard,
)
from config import (
    IS_COMPETITION_RUNNING,
)
from utils import page_config, check_password

page_config()

# 認証チェック
check_password(always_protect=True)


def show_leaderboard() -> None:
    st.title("リーダーボード")
    with st.spinner("読み込み中..."):
        leaderboard = read_leaderboard()
        if not leaderboard.empty:
            leaderboard = leaderboard.drop("email_hash", axis=1)
            if IS_COMPETITION_RUNNING:
                leaderboard = leaderboard.drop("private_score", axis=1)
                leaderboard = leaderboard.sort_values(
                    "public_score", ascending=LEADERBOARD_SORT_ASCENDING
                )
            else:
                leaderboard = leaderboard.sort_values(
                    "private_score", ascending=LEADERBOARD_SORT_ASCENDING
                )
            df = filter_leaderboard(leaderboard)
            st.dataframe(df)
        else:
            st.info("まだ投稿がありません。")


show_leaderboard()
