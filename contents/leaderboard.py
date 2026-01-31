import streamlit as st
import plotly.express as px

from custom_settings import (
    LEADERBOARD_SORT_ASCENDING,
    LEADERBOARD_SHOW_LATEST_ONLY,
    AUTH,
    read_leaderboard,
    filter_leaderboard,
)
from config import (
    IS_COMPETITION_RUNNING,
    DATA_STORE_TYPE,
)
from utils import page_config, check_password, show_register_ground_truth_message
from data_store import get_data_store

page_config()

st.title(":material/leaderboard: リーダーボード")

# 認証チェック
check_password(always_protect=True)


def show_leaderboard() -> None:
    # データストアのタイプがDBベースの場合、ground_truthの存在チェック
    if DATA_STORE_TYPE != "google_sheet":
        data_store = get_data_store()
        if not data_store.has_ground_truth():
            show_register_ground_truth_message()
            st.stop()

    with st.spinner("読み込み中..."):
        leaderboard = read_leaderboard()
        if leaderboard.empty:
            st.info("まだ投稿がありません。")
            return

        # 同一ユーザーの最新投稿のみ表示する場合
        if LEADERBOARD_SHOW_LATEST_ONLY:
            user_col = "email_hash" if AUTH else "username"
            if (
                user_col in leaderboard.columns
                and "submission_time" in leaderboard.columns
            ):
                # submission_timeが新しい順にソートし、ユーザーごとに最初の行（最新の投稿）を残す
                leaderboard = leaderboard.sort_values(
                    "submission_time", ascending=False
                ).drop_duplicates(subset=[user_col], keep="first")

        public_tab, private_tab = st.tabs([":material/public: Public", ":material/social_leaderboard: Private"])

        with public_tab:
            st.header(":material/table: Public Leaderboard")
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

            st.subheader(":material/bar_chart: スコア分布")
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
                st.info(
                    "Privateリーダーボードは、コンペティション終了後に公開されます。"
                )
            else:
                st.header(":material/table: Private Leaderboard")
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

                st.subheader(":material/scatter_plot: Public vs Private スコア")
                fig_scatter = px.scatter(
                    df_private,
                    x="public_score",
                    y="private_score",
                    title="Public Score vs Private Score",
                    labels={
                        "public_score": "Public Score",
                        "private_score": "Private Score",
                    },
                    hover_data=["username"] if not AUTH else [],
                )
                st.plotly_chart(fig_scatter, width="stretch")

                st.subheader(":material/bar_chart: スコア分布")
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
