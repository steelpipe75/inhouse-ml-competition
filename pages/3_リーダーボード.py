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
                    by=["public_score", "submission_time"],
                    ascending=[LEADERBOARD_SORT_ASCENDING, True],
                )
                rank_col_name = "暫定順位"
            else:
                leaderboard = leaderboard.sort_values(
                    by=["private_score", "submission_time"],
                    ascending=[LEADERBOARD_SORT_ASCENDING, True],
                )
                rank_col_name = "順位"
            leaderboard = leaderboard.reset_index(drop=True)
            leaderboard.index += 1
            leaderboard.insert(0, rank_col_name, leaderboard.index)

            df = filter_leaderboard(leaderboard)
            st.dataframe(df, hide_index=True)
        else:
            st.info("まだ投稿がありません。")


show_leaderboard()
