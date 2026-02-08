import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# プロジェクトルートをsys.pathに追加
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

st.set_page_config(page_title="正解データ閲覧アプリ", layout="wide")
st.title("正解データ閲覧アプリ")

st.write("このアプリでは、データストアに登録されている正解データを閲覧できます。")

if st.button("正解データを表示"):
    st.info(
        f"'{config.DATA_STORE_TYPE}' データストアから ground_truth データを読み込んでいます..."
    )

    try:
        data_store = get_data_store()
        df = data_store.read_ground_truth(config.GROUND_TRUTH_HEADER)

        if df.empty:
            st.warning("ground_truth にデータがありません。")
        else:
            st.success(f"データストアから {len(df)} 件の正解データを読み込みました。")
            st.dataframe(df)  # StreamlitでDataFrameを表示
            st.write(f"合計 {len(df)} 件のデータ。")

    except Exception as e:
        st.error(f"ground_truth データの読み込み中にエラーが発生しました: {e}")
        st.error(f"データストアの設定またはデータ形式に問題がある可能性があります。")

st.markdown("---")
st.write("ヒント: 「正解データ登録アプリ」でデータを登録してから閲覧してください。")
