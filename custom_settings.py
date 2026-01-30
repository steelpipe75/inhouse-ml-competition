from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import os
import streamlit as st

from data_store import get_data_store
from config import AUTH

# --- ユーザーが変更可能なカスタマイズ用変数 ---
LEADERBOARD_SHOW_LATEST_ONLY: bool = False  # リーダーボードに各ユーザーの最新の投稿のみを表示するか (True: 最新のみ, False: 全ての投稿)
DATA_DIR = (
    "competition_files/data"  # データ（学習・テスト・サンプル提出）のディレクトリ名
)
PROBLEM_FILE = "competition_files/content/problem.md"  # 問題説明Markdownファイルのパス
SAMPLE_SUBMISSION_FILE = os.path.join(
    DATA_DIR, "sample_submission.csv"
)  # サンプル提出ファイルのパス
HOME_CONTENT_FILE = "competition_files/content/home.md"  # Homeページのカスタマイズ用コンテンツファイルのパス
LEADERBOARD_SORT_ASCENDING: bool = (
    True  # リーダーボードのスコアソート順（True:昇順, False:降順）
)

# --- Email Hash Salt ---
if AUTH:
    try:
        EMAIL_HASH_SALT: str = st.secrets["EMAIL_HASH_SALT"]
    except KeyError:
        raise RuntimeError(
            "st.secrets に 'EMAIL_HASH_SALT' が設定されていません。ハッシュ化にはsaltが必要です。"
        )
else:
    EMAIL_HASH_SALT = ""

# --- Googleスプレッドシート関連のヘッダー定義 ---
# 投稿時の追加情報定義
# streamlitの入力ウィジェットを想定: {"id": "内部ID", "label": "表示ラベル", "type": "st.text_input", "kwargs": {}}
SUBMISSION_ADDITIONAL_INFO: List[Dict] = [
    {
        "id": "comment",
        "label": "コメント",
        "type": "text_input",
        "kwargs": {"max_chars": 200},
    },
]
_additional_columns: List[str] = [info["id"] for info in SUBMISSION_ADDITIONAL_INFO]
LEADERBOARD_HEADER: List[str] = [
    "username",
    "email_hash",
    "public_score",
    "private_score",
    "submission_time",
] + _additional_columns
GROUND_TRUTH_HEADER: List[str] = ["id", "target", "Usage"]


# --- スコアリング関数 ---
def score_submission(pred_df: pd.DataFrame, gt_df: pd.DataFrame) -> Tuple[float, float]:
    """public/privateスコアを返す (例:MAE)"""
    merged = pred_df.merge(gt_df, on="id", suffixes=("_pred", ""))

    public_mask = merged["Usage"] == "Public"
    private_mask = merged["Usage"] == "Private"

    public_score = np.mean(
        np.abs(
            merged.loc[public_mask, "target_pred"] - merged.loc[public_mask, "target"]
        )
    )
    private_score = np.mean(
        np.abs(
            merged.loc[private_mask, "target_pred"] - merged.loc[private_mask, "target"]
        )
    )

    return float(public_score), float(private_score)


# --- 正解データの読み込み ---
def read_ground_truth() -> pd.DataFrame:
    data_store = get_data_store()
    df = data_store.read_ground_truth(GROUND_TRUTH_HEADER)
    # データ型の変換
    if "id" in df.columns:
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
    if "target" in df.columns:
        df["target"] = pd.to_numeric(df["target"], errors="coerce")
    return df


# --- リーダーボードの読み込み ---
def read_leaderboard() -> pd.DataFrame:
    data_store = get_data_store()
    df = data_store.read_leaderboard(LEADERBOARD_HEADER)
    # データ型の変換
    if "public_score" in df.columns:
        df["public_score"] = pd.to_numeric(df["public_score"], errors="coerce")
    if "private_score" in df.columns:
        df["private_score"] = pd.to_numeric(df["private_score"], errors="coerce")
    return df


# --- リーダーボードに新しい投稿を書き込み ---
def write_submission(submission_data: Dict) -> None:
    data_store = get_data_store()
    user_col = "email_hash" if AUTH else "username"
    data_store.write_submission(
        submission_data,
        LEADERBOARD_HEADER,
        update_existing=False,  # 常に新しい行として追加
        user_col=user_col,
    )


# --- リーダーボードを表示するときのフィルタ ---
def filter_leaderboard(leaderboard_df: pd.DataFrame) -> pd.DataFrame:
    df = leaderboard_df.copy()

    if "submission_time" in df.columns:
        # submission_timeをdatetimeオブジェクトに変換
        # タイムゾーン情報がない場合はUTCとして解釈
        df["submission_time"] = pd.to_datetime(
            df["submission_time"], errors="coerce", utc=True
        )

        # 日本時間 (Asia/Tokyo) に変換
        df["submission_time"] = df["submission_time"].dt.tz_convert("Asia/Tokyo")

    return df
