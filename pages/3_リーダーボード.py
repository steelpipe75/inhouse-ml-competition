import streamlit as st
import plotly.express as px

from custom_settings import (
    LEADERBOARD_SORT_ASCENDING,
    SUBMISSION_UPDATE_EXISTING_USER,
    AUTH,
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
        if leaderboard.empty:
            st.info("まだ投稿がありません。")
            return

        # 同一ユーザーの最新投稿のみ表示する場合
        if SUBMISSION_UPDATE_EXISTING_USER:
            user_col = "email_hash" if AUTH else "username"
            if (
                user_col in leaderboard.columns
                and "submission_time" in leaderboard.columns
            ):
                # submission_timeが新しい順にソートし、ユーザーごとに最初の行（最新の投稿）を残す
                leaderboard = leaderboard.sort_values(
                    "submission_time", ascending=False
                ).drop_duplicates(subset=[user_col], keep="first")

        public_tab, private_tab = st.tabs(["Public", "Private"])

        with public_tab:
            st.header("Public Leaderboard")
            # Publicスコアでのリーダーボード（コンペ中・終了後にかかわらず表示）
            df_public = leaderboard.drop("email_hash", axis=1, errors="ignore")
            if "private_score" in df_public.columns:
                df_public = df_public.drop("private_score", axis=1)

            df_public = df_public.sort_values(
                by=["public_score", "submission_time"],
                ascending=[LEADERBOARD_SORT_ASCENDING, True],
            )
            df_public = df_public.reset_index(drop=True)
            df_public.index += 1
            df_public.insert(0, "暫定順位", df_public.index)

            st.dataframe(filter_leaderboard(df_public), hide_index=True)

            st.subheader("スコア分布")
            fig_public = px.histogram(
                df_public,
                x="public_score",
                nbins=20,
                title="Public Score の分布",
                labels={"public_score": "Public Score", "count": "人数"},
            )
            st.plotly_chart(fig_public, width="stretch")

        with private_tab:
            if IS_COMPETITION_RUNNING:
                st.info("Privateリーダーボードは、コンペティション終了後に公開されます。")
            else:
                st.header("Private Leaderboard")
                # Privateスコアでのリーダーボード
                df_private = leaderboard.drop("email_hash", axis=1, errors="ignore")
                df_private = df_private.sort_values(
                    by=["private_score", "submission_time"],
                    ascending=[LEADERBOARD_SORT_ASCENDING, True],
                )
                df_private = df_private.reset_index(drop=True)
                df_private.index += 1
                df_private.insert(0, "順位", df_private.index)

                st.dataframe(filter_leaderboard(df_private), hide_index=True)

                st.subheader("スコア分布")
                score_df = df_private[["public_score", "private_score"]].melt(
                    var_name="score_type", value_name="score"
                )
                fig_private = px.histogram(
                    score_df,
                    x="score",
                    color="score_type",
                    nbins=20,
                    barmode="overlay",
                    title="スコア分布",
                    labels={"score": "Score", "count": "人数"},
                )
                st.plotly_chart(fig_private, width="stretch")


show_leaderboard()
