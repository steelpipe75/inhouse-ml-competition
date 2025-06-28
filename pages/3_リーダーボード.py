import streamlit as st
import pandas as pd
import os

from config import LEADERBOARD_FILE
from custom_settings import LEADERBOARD_SORT_ASCENDING, IS_COMPETITION_RUNNING

def show_leaderboard():
    st.title("リーダーボード")
    if os.path.exists(LEADERBOARD_FILE):
        leaderboard = pd.read_csv(LEADERBOARD_FILE)
        leaderboard = leaderboard.sort_values("public_score", ascending=LEADERBOARD_SORT_ASCENDING)
        if IS_COMPETITION_RUNNING:
            st.dataframe(leaderboard[["user", "timestamp", "public_score"]])
        else:
            st.dataframe(leaderboard[["user", "timestamp", "public_score", "private_score"]])
    else:
        st.info("まだ投稿がありません。")

show_leaderboard()
