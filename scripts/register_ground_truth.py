import pandas as pd
from sqlalchemy import create_engine
import sys
from pathlib import Path
import toml

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


def get_db_url_from_secrets() -> str:
    """
    .streamlit/secrets.toml からデータベースのURLを取得します。
    """
    secrets_path = project_root / ".streamlit" / "secrets.toml"
    if not secrets_path.exists():
        print(f"警告: secrets.toml が見つかりません: {secrets_path}")
        return ""

    try:
        secrets = toml.load(secrets_path)
        db_type = config.DATA_STORE_TYPE
        
        if "connections" in secrets and db_type in secrets["connections"]:
            conn_info = secrets["connections"][db_type]
            
            if "url" in conn_info and conn_info["url"]:
                return conn_info["url"]
            
            dialect = conn_info["dialect"]
            driver = conn_info.get("driver")
            username = conn_info["username"]
            password = conn_info["password"]
            host = conn_info["host"]
            port = conn_info["port"]
            database = conn_info["database"]
            
            dialect_driver = f"{dialect}+{driver}" if driver else dialect
            return f"{dialect_driver}://{username}:{password}@{host}:{port}/{database}"

    except (toml.TomlDecodeError, KeyError) as e:
        print(f"secrets.toml の解析中にエラーが発生しました: {e}")
        return ""
    
    return ""

def register_ground_truth_from_excel():
    """
    Excelファイルから ground_truth データを読み込み、
    config.py と secrets.toml の設定に基づいてデータベースに登録します。
    """
    engine = None
    db_type = config.DATA_STORE_TYPE

    print(f"データストアタイプ: {db_type}")

    if db_type == "sqlite":
        db_path = project_root / config.DB_PATH
        print(f"SQLiteデータベースを使用します: {db_path}")

        # (SQLiteの既存のセットアップコードは省略)
        db_dir = db_path.parent
        db_dir.mkdir(parents=True, exist_ok=True)
        # ... .gitignoreの処理など
        
        engine = create_engine(f"sqlite:///{db_path}")

    elif db_type in ["mysql", "postgresql"]:
        db_url = get_db_url_from_secrets()
        if not db_url:
            print(f"エラー: .streamlit/secrets.toml から {db_type} の接続情報が見つかりませんでした。")
            sys.exit(1)
        print(f"{db_type.capitalize()}データベースを使用します: {db_url.split('@')[-1]}")
        engine = create_engine(db_url)

    else:
        print(f"エラー: サポートされていないデータストアタイプです: {db_type}")
        print("このスクリプトは 'sqlite', 'mysql', 'postgresql' のみをサポートしています。")
        sys.exit(1)

    # (以降のExcel読み込みとDB書き込み処理は変更なし)
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
