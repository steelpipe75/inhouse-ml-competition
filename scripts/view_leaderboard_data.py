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


def view_leaderboard_data():
    """
    設定されたデータストアからリーダーボードデータを読み込み、表示します。
    """
    print(f"'{config.DATA_STORE_TYPE}' データストアからリーダーボードデータを読み込んでいます...")

    try:
        data_store = get_data_store()
        df = data_store.read_leaderboard(config.LEADERBOARD_HEADER)

        if df.empty:
            print(f"リーダーボードにデータがありません。")
        else:
            print("\n--- リーダーボードデータ ---")
            # デフォルトの表示制限を解除して、全ての行と列を表示
            with pd.option_context(
                "display.max_rows", None, "display.max_columns", None
            ):
                print(df.to_string(index=False))
            print(f"\n合計 {len(df)} 件のデータ。")

    except Exception as e:
        print(f"リーダーボードデータの読み込み中にエラーが発生しました: {e}")
        print(
            f"データストアの設定またはデータ形式に問題がある可能性があります。"
        )


if __name__ == "__main__":
    view_leaderboard_data()

