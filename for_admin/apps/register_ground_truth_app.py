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
    st.info(
        "Streamlitアプリがプロジェクトのルートディレクトリから実行されているか、またはsys.pathが正しく設定されているか確認してください。"
    )
    st.stop()  # モジュールが見つからない場合はここで終了

st.set_page_config(page_title="正解データ登録アプリ", layout="wide")
st.title("正解データ登録アプリ")

st.write("正解データファイルをアップロードし、データストアに登録します。")

uploaded_file = st.file_uploader(
    "正解データファイルをアップロードしてください（.csv または .xlsx）",
    type=["csv", "xlsx"],
)

df = None
selected_sheet_name = None

if uploaded_file is not None:
    file_extension = Path(uploaded_file.name).suffix

    if file_extension == ".csv":
        try:
            df = pd.read_csv(uploaded_file)
            st.success("CSVファイルを正常に読み込みました。")
        except Exception as e:
            st.error(f"CSVファイルの読み込み中にエラーが発生しました: {e}")
    elif file_extension == ".xlsx":
        try:
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_names = excel_file.sheet_names
            if sheet_names:
                selected_sheet_name = st.selectbox(
                    "使用するシートを選択してください", sheet_names
                )
                if selected_sheet_name:
                    df = excel_file.parse(selected_sheet_name)
                    st.success(
                        f"Excelファイルからシート '{selected_sheet_name}' を正常に読み込みました。"
                    )
            else:
                st.warning("Excelファイルにシートが見つかりませんでした。")
        except Exception as e:
            st.error(f"Excelファイルの読み込み中にエラーが発生しました: {e}")
    else:
        st.error(
            "サポートされていないファイル形式です。CSVまたはXLSXファイルをアップロードしてください。"
        )

# df が存在する場合のみプレビューと登録ボタンを表示
if df is not None and not df.empty:
    st.subheader("アップロードされたデータのプレビュー")
    st.dataframe(df)

    if st.button("プレビューしたデータを登録"):
        st.info(f"データストアタイプ: {config.DATA_STORE_TYPE}")
        st.info(
            f"'{config.GROUND_TRUTH_TABLE_NAME}' または '{config.GROUND_TRUTH_WORKSHEET_NAME}' にデータを登録します..."
        )

        try:
            data_store = get_data_store()
            data_store.write_ground_truth(df, config.GROUND_TRUTH_HEADER)
            st.success(
                f"正解データの登録が完了しました。データストアに {len(df)} 件のデータが登録されました。"
            )
        except Exception as e:
            st.error(f"データストアへの書き込み中にエラーが発生しました: {e}")
            st.error(
                f"データストアの設定またはデータ形式に問題がある可能性があります。"
            )
elif uploaded_file is not None and (df is None or df.empty):
    st.warning("読み込むデータがありません、またはデータが空です。")
else:
    st.info("ファイルをアップロードしてください。")

st.markdown("---")
st.write("注意事項: この操作は、既存の正解データを上書きする可能性があります。")
