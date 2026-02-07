import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# プロジェクトルートをsys.pathに追加
# Streamlitアプリとして実行される際に、プロジェクトルートが正しく認識されるように調整
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

try:
    import config
    from data_store import get_data_store
except ImportError as e:
    st.error(f"エラー: 必要なモジュールが見つかりません。{e}")
    st.info("Streamlitアプリがプロジェクトのルートディレクトリから実行されているか、またはsys.pathが正しく設定されているか確認してください。")
    st.stop() # モジュールが見つからない場合はここで終了

st.set_page_config(page_title="正解データ登録アプリ", layout="wide")
st.title("正解データ登録アプリ")

st.write("このアプリでは、`competition_files/sample_spreadsheets.xlsx`から`ground_truth`シートのデータを読み込み、データストアに登録します。")

excel_path = project_root / "competition_files" / "sample_spreadsheets.xlsx"
sheet_name = "ground_truth"

if st.button("正解データを登録"):
    st.info(f"データストアタイプ: {config.DATA_STORE_TYPE}")
    st.info(f"Excelファイル '{excel_path}' から '{sheet_name}' シートを読み込んでいます...")

    try:
        if not excel_path.exists():
            st.error(f"エラー: Excelファイルが見つかりません: {excel_path}")
            st.stop()

        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        st.success(f"Excelファイルから {len(df)} 件のデータを正常に読み込みました。")
        st.dataframe(df.head()) # 読み込んだデータの一部を表示

        st.info(f"'{config.GROUND_TRUTH_TABLE_NAME}' または '{config.GROUND_TRUTH_WORKSHEET_NAME}' にデータを登録します...")

        data_store = get_data_store()
        data_store.write_ground_truth(df, config.GROUND_TRUTH_HEADER)
        st.success(f"正解データの登録が完了しました。データストアに {len(df)} 件のデータが登録されました。")

    except ValueError as ve:
        if "Worksheet" in str(ve) and "not found" in str(ve):
            st.error(f"エラー: Excelファイルに '{sheet_name}' シートが見つかりません。")
        else:
            st.error(f"Excelファイルの読み込み中にエラーが発生しました: {ve}")
    except Exception as e:
        st.error(f"データストアへの書き込み中にエラーが発生しました: {e}")
        st.error(f"データストアの設定またはデータ形式に問題がある可能性があります。")

st.markdown("---")
st.write("注意事項: この操作は、既存の正解データを上書きする可能性があります。")
