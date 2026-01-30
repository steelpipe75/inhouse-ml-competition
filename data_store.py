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
import os


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
        update_existing: bool,
        user_col: str,
    ):
        """投稿データを書き込む。"""
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
        update_existing: bool,
        user_col: str,
    ):
        worksheet = self._get_worksheet(self.leaderboard_worksheet_name, header=header)
        current_df = self.read_leaderboard(header)
        new_row_df = pd.DataFrame([submission_data], columns=header)

        if update_existing and not current_df.empty:
            user_identifier = submission_data.get(user_col)
            # user_colが存在し、かつ空でない場合のみ更新を試みる
            if user_identifier:
                # 文字列に変換して比較
                current_df[user_col] = current_df[user_col].astype(str)
                user_identifier = str(user_identifier)

                existing_user_mask = current_df[user_col] == user_identifier
                if existing_user_mask.any():
                    # 既存の行を更新
                    idx = current_df.index[existing_user_mask].tolist()[0]
                    # submission_dataに含まれるキーのみを更新
                    for key, value in submission_data.items():
                        if key in current_df.columns:
                            current_df.loc[idx, key] = value
                    updated_df = current_df
                else:
                    # 存在しない場合は追加
                    updated_df = pd.concat([current_df, new_row_df], ignore_index=True)
            else:
                # user_identifierがない場合は単純に追加
                updated_df = pd.concat([current_df, new_row_df], ignore_index=True)
        else:
            # 更新しないか、データが空の場合は単純に追加
            updated_df = pd.concat([current_df, new_row_df], ignore_index=True)

        set_with_dataframe(worksheet, updated_df.reindex(columns=header), resize=True)


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
        self, table_name: str, header: List[str], user_col: Optional[str] = None
    ):
        inspector = sqlalchemy.inspect(self.engine)
        if not inspector.has_table(table_name):
            meta = sqlalchemy.MetaData()

            # id列を主キーとして定義（自動インクリメント）
            columns = [
                sqlalchemy.Column(
                    "id", sqlalchemy.Integer, primary_key=True, autoincrement=True
                )
            ]
            # headerの列を汎用的なText型として追加
            columns.extend([sqlalchemy.Column(h, sqlalchemy.Text) for h in header])

            # テーブル定義
            sqlalchemy.Table(table_name, meta, *columns)

            # テーブル作成
            meta.create_all(self.engine)

            if user_col and table_name == self.leaderboard_table_name:
                with self.engine.connect() as con:
                    try:
                        # ALTER TABLE文はデータベース製品による方言の差が大きい
                        # ここでは一般的なSQL標準に近い引用符を使った構文を試す
                        con.execute(
                            sqlalchemy.text(
                                f'ALTER TABLE "{table_name}" ADD UNIQUE ("{user_col}")'
                            )
                        )
                        con.commit()
                    except SQLAlchemyError as e:
                        print(
                            f"Could not add UNIQUE constraint on {user_col}: {e}. This might be expected if the DB dialect does not support this syntax."
                        )

    def read_ground_truth(self, header: List[str]) -> pd.DataFrame:
        self._create_table_if_not_exists(self.ground_truth_table_name, header)
        try:
            return pd.read_sql(self.ground_truth_table_name, self.engine)
        except Exception as e:
            print(f"An error occurred while reading the ground truth from DB: {e}")
            return pd.DataFrame(columns=header)

    def read_leaderboard(self, header: List[str]) -> pd.DataFrame:
        self._create_table_if_not_exists(
            self.leaderboard_table_name, header, user_col="username"
        )  # ToDo: user_colを固定しない
        try:
            return pd.read_sql(self.leaderboard_table_name, self.engine)
        except Exception as e:
            print(f"An error occurred while reading the leaderboard from DB: {e}")
            return pd.DataFrame(columns=header)

    def write_submission(
        self,
        submission_data: Dict[str, Any],
        header: List[str],
        update_existing: bool,
        user_col: str,
    ):
        self._create_table_if_not_exists(self.leaderboard_table_name, header, user_col)

        user_identifier = submission_data.get(user_col)

        if update_existing and user_identifier:
            with self.engine.connect() as con:
                tbl = sqlalchemy.Table(
                    self.leaderboard_table_name,
                    sqlalchemy.MetaData(),
                    autoload_with=self.engine,
                )

                # 既存レコードの確認
                select_stmt = sqlalchemy.select(tbl).where(
                    tbl.c[user_col] == user_identifier
                )
                result = con.execute(select_stmt).fetchone()

                if result:
                    # 更新
                    update_stmt = (
                        sqlalchemy.update(tbl)
                        .where(tbl.c[user_col] == user_identifier)
                        .values(**submission_data)
                    )
                    con.execute(update_stmt)
                else:
                    # 挿入
                    insert_stmt = sqlalchemy.insert(tbl).values(**submission_data)
                    con.execute(insert_stmt)
                con.commit()
        else:
            # 単純挿入
            df = pd.DataFrame([submission_data], columns=header)
            df.to_sql(
                self.leaderboard_table_name,
                self.engine,
                if_exists="append",
                index=False,
            )


class SQLiteDataStore(BaseDBDataStore):
    """SQLiteをデータストアとして使用するクラス。"""

    def __init__(
        self,
        db_path: str,
        leaderboard_table_name: str,
        ground_truth_table_name: str,
    ):
        # データベースファイルのためのディレクトリが存在しない場合は作成
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        # データベースファイルが実際に存在するかチェック
        db_file_exists = os.path.exists(db_path)

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
