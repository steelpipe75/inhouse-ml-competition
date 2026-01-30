import pandas as pd
import sqlite3
import sys
from pathlib import Path

# プロジェクトルートをsys.pathに追加
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

try:
    import config
except ImportError:
    print("エラー: config.py が見つかりません。")
    print("このスクリプトはプロジェクトのルートディレクトリから実行するか、")
    print("プロジェクトルートが sys.path に含まれている必要があります。")
    sys.exit(1)


def view_leaderboard_data():
    """
    SQLiteデータベースからリーダーボードデータを読み込み、表示します。
    """
    db_path = project_root / config.DB_PATH
    table_name = config.LEADERBOARD_TABLE_NAME

    if not db_path.exists():
        print(f"エラー: データベースファイルが見つかりません: {db_path}")
        print("リーダーボードデータがまだ登録されていない可能性があります。")
        return

    print(f"'{db_path}' から '{table_name}' テーブルのデータを読み込んでいます...")

    try:
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

        if df.empty:
            print(f"'{table_name}' テーブルにデータがありません。")
        else:
            print("\n--- リーダーボードデータ ---")
            # デフォルトの表示制限を解除して、全ての行と列を表示
            with pd.option_context(
                "display.max_rows", None, "display.max_columns", None
            ):
                print(df.to_string(index=False))
            print(f"\n合計 {len(df)} 件のデータ。")

    except pd.io.sql.DatabaseError as e:
        print(f"データベースの読み込み中にエラーが発生しました: {e}")
        print(
            f"'{table_name}' テーブルが存在しないか、データ形式に問題がある可能性があります。"
        )
    except sqlite3.Error as e:
        print(f"データベース接続中にエラーが発生しました: {e}")


if __name__ == "__main__":
    view_leaderboard_data()
