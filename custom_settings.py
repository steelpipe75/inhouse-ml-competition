from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import os
import streamlit as st

from utils import (
    read_ground_truth_core,
    read_leaderboard_core,
    write_submission_preproc,
    write_submission_core,
)
from config import IS_COMPETITION_RUNNING

# --- ユーザーが変更可能なカスタマイズ用変数 ---
SUBMISSION_UPDATE_EXISTING_USER: bool = (
   False  # 投稿時に既存ユーザーがいた場合にスコアを更新するか (True: 更新, False: 新しい行として追加)
)
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
    df = read_ground_truth_core(GROUND_TRUTH_HEADER)
    # データ型の変換
    if "id" in df.columns:
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
    if "target" in df.columns:
        df["target"] = pd.to_numeric(df["target"], errors="coerce")
    return df


# --- リーダーボードの読み込み ---
def read_leaderboard() -> pd.DataFrame:
    df = read_leaderboard_core(LEADERBOARD_HEADER)
    # データ型の変換
    if "public_score" in df.columns:
        df["public_score"] = pd.to_numeric(df["public_score"], errors="coerce")
    if "private_score" in df.columns:
        df["private_score"] = pd.to_numeric(df["private_score"], errors="coerce")
    return df


# --- リーダーボードに新しい投稿を書き込み ---
def write_submission(submission_data: Dict) -> None:
    worksheet, df = write_submission_preproc(LEADERBOARD_HEADER)

    username = submission_data.get("username")
    if not username:
        st.error("投稿データにユーザー名が含まれていません。")
        return

    # DataFrameに変換しやすいように、すべての値をリストにする
    new_df = pd.DataFrame([submission_data])

    # 既存ユーザーがいて、かつ更新設定が有効な場合
    if SUBMISSION_UPDATE_EXISTING_USER and username in df["username"].values:
        # 既存の行を更新
        update_cols = [col for col in submission_data.keys() if col != "username"]
        for col in update_cols:
            df.loc[df["username"] == username, col] = submission_data[col]
    else:
        # 新しい行を追加
        if df.empty:
            df = new_df
        else:
            df = pd.concat([df, new_df], ignore_index=True)

    # ヘッダー順にカラムを並び替え
    df = df.reindex(columns=LEADERBOARD_HEADER)

    write_submission_core(worksheet, df)


# --- リーダーボードを表示するときのフィルタ ---
def filter_leaderboard(leaderboard_df: pd.DataFrame) -> pd.DataFrame:
    if IS_COMPETITION_RUNNING:
        df = leaderboard_df.drop("private_score", axis=1)
    else:
        df = leaderboard_df

    df = df.copy()

    if "submission_time" in df.columns:
        # submission_timeをdatetimeオブジェクトに変換
        # タイムゾーン情報がない場合はUTCとして解釈
        df["submission_time"] = pd.to_datetime(
            df["submission_time"], errors="coerce", utc=True
        )

        # 日本時間 (Asia/Tokyo) に変換
        df["submission_time"] = df["submission_time"].dt.tz_convert("Asia/Tokyo")

    return df
