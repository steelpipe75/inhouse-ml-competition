import streamlit as st
import plotly.express as px

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
            leaderboard_display = leaderboard.drop("email_hash", axis=1)
            if IS_COMPETITION_RUNNING:
                leaderboard_display = leaderboard_display.drop("private_score", axis=1)
                leaderboard_display = leaderboard_display.sort_values(
                    by=["public_score", "submission_time"],
                    ascending=[LEADERBOARD_SORT_ASCENDING, True],
                )
                rank_col_name = "暫定順位"
            else:
                leaderboard_display = leaderboard_display.sort_values(
                    by=["private_score", "submission_time"],
                    ascending=[LEADERBOARD_SORT_ASCENDING, True],
                )
                rank_col_name = "順位"
            leaderboard_display = leaderboard_display.reset_index(drop=True)
            leaderboard_display.index += 1
            leaderboard_display.insert(0, rank_col_name, leaderboard_display.index)

            df = filter_leaderboard(leaderboard_display)
            st.dataframe(df, hide_index=True)

            st.subheader("スコア分布")

            if IS_COMPETITION_RUNNING:
                fig = px.histogram(
                    leaderboard_display,
                    x="public_score",
                    nbins=20,
                    title="Public Score の分布",
                    labels={"public_score": "Public Score", "count": "人数"},
                )
            else:
                score_df = leaderboard_display[["public_score", "private_score"]].melt(
                    var_name="score_type", value_name="score"
                )
                fig = px.histogram(
                    score_df,
                    x="score",
                    color="score_type",
                    nbins=20,
                    barmode="overlay",
                    title="スコア分布",
                    labels={"score": "Score", "count": "人数"},
                )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("まだ投稿がありません。")


show_leaderboard()
