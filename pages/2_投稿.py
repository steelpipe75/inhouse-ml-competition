import streamlit as st
import pandas as pd
import os
import datetime

from config import SUBMISSION_DIR, LEADERBOARD_FILE
from custom_settings import (
    SAMPLE_SUBMISSION_FILE,
    GROUND_TRUTH_FILE,
    score_submission,
    IS_COMPETITION_RUNNING,
)

os.makedirs(SUBMISSION_DIR, exist_ok=True)

def update_leaderboard(username, public_score, private_score):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = pd.DataFrame(
        [[username, now, public_score, private_score]],
        columns=["user", "timestamp", "public_score", "private_score"]
    )
    if os.path.exists(LEADERBOARD_FILE):
        leaderboard = pd.read_csv(LEADERBOARD_FILE)
        leaderboard = pd.concat([leaderboard, new_entry], ignore_index=True)
    else:
        leaderboard = new_entry
    leaderboard.to_csv(LEADERBOARD_FILE, index=False)

def show_submission():
    st.title("予測結果の投稿")
    username = st.text_input("ユーザー名")
    uploaded_file = st.file_uploader("予測CSVをアップロード", type="csv")

    if st.button("投稿する"):
        if not username:
            st.error("ユーザー名を入力してください。")
        elif not uploaded_file:
            st.error("CSVファイルをアップロードしてください。")
        else:
            try:
                submission = pd.read_csv(uploaded_file)
                sample = pd.read_csv(SAMPLE_SUBMISSION_FILE)
                ground_truth = pd.read_csv(GROUND_TRUTH_FILE)

                if list(submission.columns) != list(sample.columns):
                    st.error("カラムが期待する形と一致していません。")
                else:
                    public_score, private_score = score_submission(submission, ground_truth)
                    filepath = os.path.join(
                        SUBMISSION_DIR,
                        f"{username}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                    )
                    submission.to_csv(filepath, index=False)
                    update_leaderboard(username, public_score, private_score)
                    if IS_COMPETITION_RUNNING:
                        st.success(
                            f"投稿完了！Publicスコア: {public_score:.4f}"
                        )
                    else:
                        st.success(
                            f"投稿完了！Publicスコア: {public_score:.4f} / Privateスコア: {private_score:.4f}"
                        )
            except Exception as e:
                st.error(f"スコア計算中にエラー: {e}")

show_submission()
