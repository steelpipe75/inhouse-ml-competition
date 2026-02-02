import pandas as pd
from sqlalchemy import create_engine
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
    Excelファイルから ground_truth データを読み込み、
    config.py の設定に基づいてデータベースに登録します。
    """
    engine = None
    db_type = config.DATA_STORE_TYPE

    print(f"データストアタイプ: {db_type}")

    if db_type == "sqlite":
        db_path = project_root / config.DB_PATH
        print(f"SQLiteデータベースを使用します: {db_path}")

        # データベースファイルの親ディレクトリが存在しない場合は作成
        db_dir = db_path.parent
        dir_existed_before = db_dir.exists()
        db_dir.mkdir(parents=True, exist_ok=True)

        # .gitignore を処理
        db_filename = db_path.name
        gitignore_path = db_dir / ".gitignore"

        if not dir_existed_before:
            gitignore_path.write_text("*\n", encoding="utf-8")
        else:
            try:
                content = gitignore_path.read_text(encoding="utf-8")
            except FileNotFoundError:
                content = ""

            if db_filename not in content:
                with gitignore_path.open("a", encoding="utf-8") as f:
                    f.write(f"\n{db_filename}\n")
        
        engine = create_engine(f"sqlite:///{db_path}")

    elif db_type == "mysql":
        db_url = config.DB_URL
        if not db_url:
            print("エラー: config.py で DB_URL が設定されていません。")
            sys.exit(1)
        print(f"MySQLデータベースを使用します: {db_url.split('@')[-1]}")
        engine = create_engine(db_url)

    else:
        print(f"エラー: サポートされていないデータストアタイプです: {db_type}")
        print("このスクリプトは 'sqlite' または 'mysql' のみをサポートしています。")
        sys.exit(1)

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

    print(f"'{table_name}' テーブルにデータを登録します...")

    try:
        with engine.connect() as conn:
            df.to_sql(table_name, conn, if_exists="replace", index=False)
        print("登録が完了しました。")
        print(f"'{table_name}' テーブルに {len(df)} 件のデータが登録されました。")

    except Exception as e:
        print(f"データベースへの書き込み中にエラーが発生しました: {e}")


if __name__ == "__main__":
    register_ground_truth_from_excel()
