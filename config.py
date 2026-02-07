import streamlit as st
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import os

from data_store import get_data_store
# --- App Navigation ---
def _get_NAVIGATION_PAGES():
    return [
        st.Page("contents/home.py", title="Home", icon=":material/home:"),
        st.Page(
            "contents/problem.py", title="概要・データ", icon=":material/menu_book:"
        ),
        st.Page("contents/submit.py", title="予測結果の投稿", icon=":material/send:"),
        st.Page(
            "contents/leaderboard.py",
            title="リーダーボード",
            icon=":material/leaderboard:",
        ),
    ]

def get_APP_NAVIGATION_PAGES():
    APP_NAVIGATION_PAGES = _get_NAVIGATION_PAGES() + [
            st.Page(
                "competition_files/contents/playground.py", title="playground", icon=":material/terminal:"
            ),
        ]

    return APP_NAVIGATION_PAGES

# --- Page Settings ---
PAGE_TITLE = "内輪向け機械学習コンペアプリ"

# --- Auth Settings ---
try:
    AUTH = st.secrets["AUTH"]
except (KeyError, FileNotFoundError):
    AUTH = False

PROTECT_ALL_PAGES = False  # Trueの場合、すべてのページを保護します。Falseの場合、投稿とリーダーボードページのみを保護します。

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

# --- Competition Settings ---
IS_COMPETITION_RUNNING = (
    False  # コンペ開催中かどうかのフラグ（True:開催中, False:終了後）
)

# --- Data Store Settings ---
# データストアの種類を選択: "google_sheet", "sqlite", "mysql", "postgresql"
DATA_STORE_TYPE = "postgresql"

# Google Sheets specific settings
SPREADSHEET_NAME = "sample_spreadsheets"  # ここにスプレッドシート名を入力してください
LEADERBOARD_WORKSHEET_NAME = "leaderboard"  # リーダーボード用のワークシート名
GROUND_TRUTH_WORKSHEET_NAME = "ground_truth"  # 正解データ用のワークシート名

# Database specific settings
DB_PATH = "db/competition.db"  # For SQLite

# DB_URL is constructed from st.secrets for security
DB_URL = ""
if DATA_STORE_TYPE in ["postgresql", "mysql"]:
    try:
        # st.secretsからデータベース接続情報を取得
        conn_info = st.secrets["connections"][DATA_STORE_TYPE]
        
        # 完全なURLが設定されていればそれを使用
        if "url" in conn_info and conn_info["url"]:
            DB_URL = conn_info["url"]
        # そうでなければ、各パーツからURLを組み立てる
        else:
            dialect = conn_info["dialect"]
            driver = conn_info.get("driver")
            username = conn_info["username"]
            password = conn_info["password"]
            host = conn_info["host"]
            port = conn_info["port"]
            database = conn_info["database"]
            
            if driver:
                dialect_driver = f"{dialect}+{driver}"
            else:
                dialect_driver = dialect

            DB_URL = f"{dialect_driver}://{username}:{password}@{host}:{port}/{database}"

    except (FileNotFoundError, KeyError):
        # Streamlit Community Cloud 環境以外でsecrets.tomlがない場合や、
        # 必要なキーが設定されていない場合は、DB_URLは空文字列のままとなる
        # scripts/register_ground_truth.py などは別途 secrets.toml を直接読み込む
        pass

# Database Table Names
LEADERBOARD_TABLE_NAME = "leaderboard"
GROUND_TRUTH_TABLE_NAME = "ground_truth"


# --- Competition Specific Customization ---

# Directory and File Paths
DATA_DIR = (
    "competition_files/data"  # データ（学習・テスト・サンプル提出）のディレクトリ名
)
PROBLEM_FILE = "competition_files/contents/problem.md"  # 問題説明Markdownファイルのパス
SAMPLE_SUBMISSION_FILE = os.path.join(
    DATA_DIR, "sample_submission.csv"
)  # サンプル提出ファイルのパス
HOME_CONTENT_FILE = "competition_files/contents/home.md"  # Homeページのカスタマイズ用コンテンツファイルのパス

# Leaderboard Settings
LEADERBOARD_SHOW_LATEST_ONLY: bool = False  # リーダーボードに各ユーザーの最新の投稿のみを表示するか (True: 最新のみ, False: 全ての投稿)
LEADERBOARD_SORT_ASCENDING: bool = (
    True  # リーダーボードのスコアソート順（True:昇順, False:降順）
)

# --- Submission and Header Definitions ---
# Submission additional info definition
SUBMISSION_ADDITIONAL_INFO: List[Dict] = [
    {
        "id": "comment",
        "label": "コメント",
        "type": "text_input",
        "kwargs": {"max_chars": 200, "icon": ":material/sticky_note_2:"},
    },
]
_additional_columns: List[str] = [info["id"] for info in SUBMISSION_ADDITIONAL_INFO]

# Header definitions for data stores
LEADERBOARD_HEADER: List[str] = [
    "username",
    "email_hash",
    "public_score",
    "private_score",
    "submission_time",
    "is_competition_running",
] + _additional_columns
GROUND_TRUTH_HEADER: List[str] = ["id", "target", "Usage"]


# --- Scoring Function ---
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


# --- Data Reading/Writing Functions ---


def read_ground_truth() -> pd.DataFrame:
    """正解データの読み込み"""
    data_store = get_data_store()
    df = data_store.read_ground_truth(GROUND_TRUTH_HEADER)
    # データ型の変換
    if "id" in df.columns:
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
    if "target" in df.columns:
        df["target"] = pd.to_numeric(df["target"], errors="coerce")
    return df


def read_leaderboard() -> pd.DataFrame:
    """リーダーボードの読み込み"""
    data_store = get_data_store()
    df = data_store.read_leaderboard(LEADERBOARD_HEADER)
    # データ型の変換
    if "public_score" in df.columns:
        df["public_score"] = pd.to_numeric(df["public_score"], errors="coerce")
    if "private_score" in df.columns:
        df["private_score"] = pd.to_numeric(df["private_score"], errors="coerce")
    return df


def write_submission(submission_data: Dict) -> None:
    """リーダーボードに新しい投稿を書き込み"""
    data_store = get_data_store()
    data_store.write_submission(
        submission_data,
        LEADERBOARD_HEADER,
    )


# --- Leaderboard Filtering ---
def filter_leaderboard(leaderboard_df: pd.DataFrame) -> pd.DataFrame:
    """リーダーボードを表示するときのフィルタ"""
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
