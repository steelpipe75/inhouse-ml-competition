
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


def register_ground_truth_from_excel():
    """
    Excelファイルから ground_truth データを読み込み、SQLiteデータベースに登録します。
    """
    db_path = project_root / config.DB_PATH
    
    # データベースファイルの親ディレクトリが存在しない場合は作成
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    table_name = config.GROUND_TRUTH_TABLE_NAME
    excel_path = project_root / "competition_files" / "sample_spreadsheets.xlsx"
    sheet_name = "ground_truth"

    print(f"Excelファイル '{excel_path}' から '{sheet_name}' シートを読み込んでいます...")

    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
    except FileNotFoundError:
        print(f"エラー: Excelファイルが見つかりません: {excel_path}")
        return
    except Exception as e:
        if isinstance(e, ValueError) and "Worksheet" in str(e) and "not found" in str(e):
            print(f"エラー: Excelファイルに '{sheet_name}' シートが見つかりません。")
        else:
            print(f"Excelファイルの読み込み中にエラーが発生しました: {e}")
        return

    print(f"'{db_path}' の '{table_name}' テーブルにデータを登録します...")

    try:
        with sqlite3.connect(db_path) as conn:
            df.to_sql(table_name, conn, if_exists="replace", index=False)
        print("登録が完了しました。")
        print(f"'{table_name}' テーブルに {len(df)} 件のデータが登録されました。")

    except sqlite3.Error as e:
        print(f"データベースへの書き込み中にエラーが発生しました: {e}")


if __name__ == "__main__":
    register_ground_truth_from_excel()
