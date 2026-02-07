"""
データ永続化層の抽象化モジュール。
設定に応じて、Googleスプレッドシート、SQLite、MySQL、PostgreSQLなどの
異なるデータソースへのアクセスを切り替えます。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from google.oauth2.service_account import Credentials
import streamlit as st
from gspread.worksheet import Worksheet
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path


# スコープ（権限）の設定
SCOPES: List[str] = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class DataStore(ABC):
    """データストアの抽象基底クラス。"""

    @abstractmethod
    def read_ground_truth(self, header: List[str]) -> pd.DataFrame:
        """正解データを読み込む。"""
        pass

    @abstractmethod
    def read_leaderboard(self, header: List[str]) -> pd.DataFrame:
        """リーダーボードのデータを読み込む。"""
        pass

    @abstractmethod
    def write_submission(
        self,
        submission_data: Dict[str, Any],
        header: List[str],
    ):
        """投稿データを書き込む。"""
        pass

    @abstractmethod
    def write_ground_truth(self, df: pd.DataFrame, header: List[str]):
        """正解データを書き込む。"""
        pass

    @abstractmethod
    def has_ground_truth(self) -> bool:
        """正解データが登録されているかを確認する。"""
        pass


class GoogleSheetDataStore(DataStore):
    """Googleスプレッドシートをデータストアとして使用するクラス。"""

    def __init__(
        self,
        spreadsheet_name: str,
        leaderboard_worksheet_name: str,
        ground_truth_worksheet_name: str,
    ):
        self.spreadsheet_name = spreadsheet_name
        self.leaderboard_worksheet_name = leaderboard_worksheet_name
        self.ground_truth_worksheet_name = ground_truth_worksheet_name
        self.gc = self._get_gspread_client()

    def _get_gspread_client(self) -> gspread.Client:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES
        )
        return gspread.authorize(creds)

    def _get_worksheet(
        self, worksheet_name: str, header: Optional[List[str]] = None
    ) -> Worksheet:
        try:
            spreadsheet = self.gc.open(self.spreadsheet_name)
        except gspread.SpreadsheetNotFound:
            spreadsheet = self.gc.create(self.spreadsheet_name)
            spreadsheet.share(
                self.gc.auth.service_account_email, perm_type="user", role="writer"
            )

        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            if header is None:
                raise ValueError("Worksheet does not exist and no header is provided.")
            worksheet = spreadsheet.add_worksheet(
                title=worksheet_name, rows="1", cols=str(len(header))
            )
            worksheet.update("A1", [header])
        return worksheet

    def has_ground_truth(self) -> bool:
        """正解データがスプレッドシートに1行以上存在するか確認する。"""
        try:
            spreadsheet = self.gc.open(self.spreadsheet_name)
            worksheet = spreadsheet.worksheet(self.ground_truth_worksheet_name)
            # ヘッダー行を除いて1行以上あればTrue
            return worksheet.row_count > 1
        except (gspread.SpreadsheetNotFound, gspread.WorksheetNotFound):
            return False
        except Exception:
            return False

    def read_ground_truth(self, header: List[str]) -> pd.DataFrame:
        try:
            worksheet = self._get_worksheet(
                self.ground_truth_worksheet_name, header=header
            )
            df = get_as_dataframe(worksheet, usecols=list(range(len(header))), header=0)
            return df.dropna(how="all")
        except Exception as e:
            print(f"An error occurred while reading the ground truth: {e}")
            return pd.DataFrame(columns=header)

    def read_leaderboard(self, header: List[str]) -> pd.DataFrame:
        try:
            worksheet = self._get_worksheet(
                self.leaderboard_worksheet_name, header=header
            )
            df = get_as_dataframe(worksheet, usecols=list(range(len(header))), header=0)
            return df.dropna(how="all")
        except Exception as e:
            print(f"An error occurred while reading the leaderboard: {e}")
            return pd.DataFrame(columns=header)

    def write_submission(
        self,
        submission_data: Dict[str, Any],
        header: List[str],
    ):
        worksheet = self._get_worksheet(self.leaderboard_worksheet_name, header=header)

        # 常に新しい行として追加する
        current_df = self.read_leaderboard(header)
        new_row_df = pd.DataFrame([submission_data], columns=header)
        updated_df = pd.concat([current_df, new_row_df], ignore_index=True)

        set_with_dataframe(worksheet, updated_df.reindex(columns=header), resize=True)

    def write_ground_truth(self, df: pd.DataFrame, header: List[str]):
        worksheet = self._get_worksheet(self.ground_truth_worksheet_name, header=header)
        # 既存データを上書きする
        set_with_dataframe(worksheet, df.reindex(columns=header), row=1, col=1, include_column_header=True, resize=True)


class BaseDBDataStore(DataStore):
    """SQLiteやRDBなど、SQLAlchemyを使用するデータベースの共通基底クラス。"""

    def __init__(
        self,
        engine: sqlalchemy.engine.Engine,
        leaderboard_table_name: str,
        ground_truth_table_name: str,
    ):
        self.engine = engine
        self.leaderboard_table_name = leaderboard_table_name
        self.ground_truth_table_name = ground_truth_table_name

    def has_ground_truth(self) -> bool:
        """正解データがテーブルに1件以上存在するかを確認する。"""
        inspector = sqlalchemy.inspect(self.engine)
        if not inspector.has_table(self.ground_truth_table_name):
            return False
        try:
            with self.engine.connect() as con:
                # テーブルが存在する場合、行数を数える
                count = con.execute(
                    sqlalchemy.text(
                        f"SELECT COUNT(1) FROM {self.ground_truth_table_name}"
                    )
                ).scalar_one_or_none()
                return (count or 0) > 0
        except SQLAlchemyError:
            # クエリ実行時エラー
            return False

    def _create_table_if_not_exists(
        self,
        table_name: str,
        header: List[str],
        is_ground_truth_table: bool = False,
    ):
        # ヘッダーに予約語 "id" が含まれていないかチェック（大文字小文字を区別しない）
        # ground_truth_tableの場合を除外
        if not is_ground_truth_table and "id" in [h.lower() for h in header]:
            raise ValueError(
                "リーダーボードのヘッダーに 'id' という列名が含まれています。"
                "この名前はデータベースの自動採番主キーとして予約されているため使用できません。列名を変更してください。"
            )

        inspector = sqlalchemy.inspect(self.engine)
        if not inspector.has_table(table_name):
            meta = sqlalchemy.MetaData()
            columns = []
            table_args = []

            if is_ground_truth_table:
                # ground_truthテーブルの場合
                if "id" not in [h.lower() for h in header]:
                    raise ValueError(
                        "ground_truthテーブルのヘッダーには 'id' 列が含まれている必要があります。"
                    )
                for h in header:
                    is_pk = h.lower() == "id"
                    # ground_truthのidは整数とは限らないため、Text型を主キーにする
                    columns.append(
                        sqlalchemy.Column(h, sqlalchemy.Text, primary_key=is_pk)
                    )
            else:
                # leaderboardテーブルなどの場合
                # id列を主キーとして定義（自動インクリメント）
                columns.append(
                    sqlalchemy.Column(
                        "id", sqlalchemy.Integer, primary_key=True, autoincrement=True
                    )
                )
                # headerの列を汎用的なText型として追加
                columns.extend([sqlalchemy.Column(h, sqlalchemy.Text) for h in header])

            # テーブル定義
            sqlalchemy.Table(table_name, meta, *columns, *table_args)

            # テーブル作成
            meta.create_all(self.engine)

    def read_ground_truth(self, header: List[str]) -> pd.DataFrame:
        self._create_table_if_not_exists(
            self.ground_truth_table_name, header, is_ground_truth_table=True
        )
        try:
            return pd.read_sql(self.ground_truth_table_name, self.engine)
        except Exception as e:
            print(f"An error occurred while reading the ground truth from DB: {e}")
            return pd.DataFrame(columns=header)

    def read_leaderboard(self, header: List[str]) -> pd.DataFrame:
        self._create_table_if_not_exists(self.leaderboard_table_name, header)
        try:
            df = pd.read_sql(self.leaderboard_table_name, self.engine)
            # 自動インクリメントのid列は表示しない
            if "id" in df.columns:
                df = df.drop("id", axis=1)
            return df
        except Exception as e:
            print(f"An error occurred while reading the leaderboard from DB: {e}")
            return pd.DataFrame(columns=header)

    def write_submission(
        self,
        submission_data: Dict[str, Any],
        header: List[str],
    ):
        self._create_table_if_not_exists(self.leaderboard_table_name, header)

        # 常に新しい行として追加（INSERT）する
        df = pd.DataFrame([submission_data], columns=header)
        df.to_sql(
            self.leaderboard_table_name,
            self.engine,
            if_exists="append",
            index=False,
        )

    def write_ground_truth(self, df: pd.DataFrame, header: List[str]):
        self._create_table_if_not_exists(
            self.ground_truth_table_name, header, is_ground_truth_table=True
        )
        # 既存データを上書きする
        df.to_sql(
            self.ground_truth_table_name, self.engine, if_exists="replace", index=False
        )


class SQLiteDataStore(BaseDBDataStore):
    """SQLiteをデータストアとして使用するクラス。"""

    def __init__(
        self,
        db_path: str,
        leaderboard_table_name: str,
        ground_truth_table_name: str,
    ):
        db_path_obj = Path(db_path)
        db_dir = db_path_obj.parent

        dir_existed_before = db_dir.exists()
        db_dir.mkdir(parents=True, exist_ok=True)

        # .gitignore を処理
        db_filename = db_path_obj.name
        gitignore_path = db_dir / ".gitignore"

        if not dir_existed_before:
            # ディレクトリが新規作成された場合、'*'を書き込む
            gitignore_path.write_text("*\n", encoding="utf-8")
        else:
            # ディレクトリが既存の場合、dbファイル名のみを追記
            try:
                content = gitignore_path.read_text(encoding="utf-8")
            except FileNotFoundError:
                content = ""

            if db_filename not in content:
                with gitignore_path.open("a", encoding="utf-8") as f:
                    f.write(f"\n{db_filename}\n")

        # データベースファイルが実際に存在するかチェック
        db_file_exists = db_path_obj.exists()

        engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")

        # データベースファイルが存在しなかった場合、メッセージを表示
        if not db_file_exists:
            st.error(
                f"データベースファイルが存在しなかったため、新しいファイルを作成しました: `{db_path}`"
            )

        super().__init__(engine, leaderboard_table_name, ground_truth_table_name)


class RDBDataStore(BaseDBDataStore):
    """MySQL/PostgreSQLなどのリレーショナルデータベースをデータストアとして使用するクラス。"""

    def __init__(
        self, db_url: str, leaderboard_table_name: str, ground_truth_table_name: str
    ):
        engine = sqlalchemy.create_engine(db_url)
        super().__init__(engine, leaderboard_table_name, ground_truth_table_name)


_data_store_instance = None


def get_data_store() -> DataStore:
    """
    設定に基づいてデータストアのシングルトンインスタンスを返すファクトリ関数。
    """
    global _data_store_instance
    if _data_store_instance is None:
        from config import (
            DATA_STORE_TYPE,
            SPREADSHEET_NAME,
            LEADERBOARD_WORKSHEET_NAME,
            GROUND_TRUTH_WORKSHEET_NAME,
            DB_PATH,
            DB_URL,
            LEADERBOARD_TABLE_NAME,
            GROUND_TRUTH_TABLE_NAME,
        )

        if DATA_STORE_TYPE == "google_sheet":
            _data_store_instance = GoogleSheetDataStore(
                spreadsheet_name=SPREADSHEET_NAME,
                leaderboard_worksheet_name=LEADERBOARD_WORKSHEET_NAME,
                ground_truth_worksheet_name=GROUND_TRUTH_WORKSHEET_NAME,
            )
        elif DATA_STORE_TYPE == "sqlite":
            _data_store_instance = SQLiteDataStore(
                db_path=DB_PATH,
                leaderboard_table_name=LEADERBOARD_TABLE_NAME,
                ground_truth_table_name=GROUND_TRUTH_TABLE_NAME,
            )
        elif DATA_STORE_TYPE in ["mysql", "postgresql"]:
            _data_store_instance = RDBDataStore(
                db_url=DB_URL,
                leaderboard_table_name=LEADERBOARD_TABLE_NAME,
                ground_truth_table_name=GROUND_TRUTH_TABLE_NAME,
            )
        else:
            raise ValueError(f"Unsupported DATA_STORE_TYPE: {DATA_STORE_TYPE}")
    return _data_store_instance
