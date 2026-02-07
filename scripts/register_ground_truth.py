import pandas as pd
import sys
from pathlib import Path

# プロジェクトルートをsys.pathに追加
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

try:
    import config
    from data_store import get_data_store
except ImportError as e:
    print(f"エラー: 必要なモジュールが見つかりません。{e}")
    print("このスクリプトはプロジェクトのルートディレクトリから実行するか、")
    print("プロジェクトルートが sys.path に含まれている必要があります。")
    sys.exit(1)


def register_ground_truth_from_excel():
    """
    Excelファイルから ground_truth データを読み込み、
    config.py で設定されたデータストアに登録します。
    """
    db_type = config.DATA_STORE_TYPE

    print(f"データストアタイプ: {db_type}")

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

    print(f"'{config.GROUND_TRUTH_TABLE_NAME}' または '{config.GROUND_TRUTH_WORKSHEET_NAME}' にデータを登録します...")

    try:
        data_store = get_data_store()
        data_store.write_ground_truth(df, config.GROUND_TRUTH_HEADER)
        print("登録が完了しました。")
        print(f"データストアに {len(df)} 件のデータが登録されました。")

    except Exception as e:
        print(f"データストアへの書き込み中にエラーが発生しました: {e}")


if __name__ == "__main__":
    register_ground_truth_from_excel()
