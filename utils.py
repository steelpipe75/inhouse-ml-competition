from typing import List, Optional, Tuple
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from google.oauth2.service_account import Credentials
import streamlit as st
from gspread.worksheet import Worksheet

from config import (
    SPREADSHEET_NAME,
    LEADERBOARD_WORKSHEET_NAME,
    GROUND_TRUTH_WORKSHEET_NAME,
)

# スコープ（権限）の設定
SCOPES: List[str] = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_worksheet(
    worksheet_name: str, header: Optional[List[str]] = None
) -> Worksheet:
    """
    サービスアカウント情報を使用して認証し、指定されたワークシートを取得します。
    ワークシートが存在しない場合は、指定されたヘッダーで新規作成します。
    """
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    gc = gspread.authorize(creds)

    try:
        spreadsheet = gc.open(SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        spreadsheet = gc.create(SPREADSHEET_NAME)
        spreadsheet.share(creds.service_account_email, perm_type="user", role="writer")

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        if header is None:
            raise ValueError("ワークシートが存在せず、ヘッダーも指定されていません。")

        worksheet = spreadsheet.add_worksheet(
            title=worksheet_name, rows="1", cols=str(len(header))
        )
        # ヘッダー行を書き込み
        worksheet.update("A1", [header])

    return worksheet


def read_ground_truth_core(GROUND_TRUTH_HEADER: List[str]) -> pd.DataFrame:
    """
    Googleスプレッドシートから正解データを読み込み、Pandas DataFrameとして返します。
    """
    try:
        worksheet = get_worksheet(
            GROUND_TRUTH_WORKSHEET_NAME, header=GROUND_TRUTH_HEADER
        )
        df = get_as_dataframe(
            worksheet, usecols=list(range(len(GROUND_TRUTH_HEADER))), header=0
        )
        # 空の行を除外
        df = df.dropna(how="all")
        return df
    except Exception as e:
        print(f"An error occurred while reading the ground truth: {e}")
        return pd.DataFrame(columns=GROUND_TRUTH_HEADER)


def read_leaderboard_core(LEADERBOARD_HEADER: List[str]) -> pd.DataFrame:
    """
    Googleスプレッドシートからリーダーボードのデータを読み込み、Pandas DataFrameとして返します。
    """
    try:
        worksheet = get_worksheet(LEADERBOARD_WORKSHEET_NAME, header=LEADERBOARD_HEADER)
        df = get_as_dataframe(
            worksheet, usecols=list(range(len(LEADERBOARD_HEADER))), header=0
        )
        # 空の行を除外
        df = df.dropna(how="all")
        return df
    except Exception as e:
        print(f"An error occurred while reading the leaderboard: {e}")
        # エラーが発生した場合やシートが空の場合も、空のDataFrameを返す
        return pd.DataFrame(columns=LEADERBOARD_HEADER)


def write_submission_preproc(
    LEADERBOARD_HEADER: List[str]
) -> Tuple[Worksheet, pd.DataFrame]:
    worksheet = get_worksheet(LEADERBOARD_WORKSHEET_NAME, header=LEADERBOARD_HEADER)
    df = read_leaderboard_core(LEADERBOARD_HEADER)
    return worksheet, df


def write_submission_core(worksheet: Worksheet, df: pd.DataFrame) -> None:
    # スプレッドシート全体を更新
    set_with_dataframe(worksheet, df, resize=True)
