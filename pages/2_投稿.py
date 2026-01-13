import streamlit as st
import pandas as pd
import datetime
from typing import Dict

from custom_settings import (
    SAMPLE_SUBMISSION_FILE,
    SUBMISSION_ADDITIONAL_INFO,
    score_submission,
    read_ground_truth,
    write_submission,
)
from config import IS_COMPETITION_RUNNING


def render_additional_inputs() -> Dict:
    """
    custom_settings.pyのSUBMISSION_ADDITIONAL_INFOに基づいて、
    追加の入力ウィジェットをレンダリングし、その結果を辞書として返す。
    """
    additional_data = {}
    for item in SUBMISSION_ADDITIONAL_INFO:
        input_type = item.get("type", "text_input")
        label = item.get("label", "")
        item_id = item.get("id", "")
        kwargs = item.get("kwargs", {})

        if hasattr(st, input_type):
            input_func = getattr(st, input_type)
            additional_data[item_id] = input_func(label, **kwargs)
        else:
            st.warning(f"指定された入力タイプ '{input_type}' は無効です。")
    return additional_data


def show_submission() -> None:
    st.title("予測結果の投稿")
    username = st.text_input("ユーザー名")

    # 追加の入力欄を動的に生成
    additional_inputs = render_additional_inputs()

    uploaded_file = st.file_uploader("予測CSVをアップロード", type="csv")

    if st.button("投稿する"):
        if not username:
            st.error("ユーザー名を入力してください。")
        elif not uploaded_file:
            st.error("CSVファイルをアップロードしてください。")
        else:
            try:
                submission_df = pd.read_csv(uploaded_file)
                sample_df = pd.read_csv(SAMPLE_SUBMISSION_FILE)
                ground_truth_df = read_ground_truth()

                if list(submission_df.columns) != list(sample_df.columns):
                    st.error("カラムが期待する形と一致していません。")
                else:
                    public_score, private_score = score_submission(
                        submission_df, ground_truth_df
                    )

                    # 投稿データを作成
                    submission_data = {
                        "username": username,
                        "public_score": public_score,
                        "private_score": private_score,
                        "submission_time": datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    }
                    submission_data.update(additional_inputs)

                    # データを書き込み
                    write_submission(submission_data)

                    if IS_COMPETITION_RUNNING:
                        st.success(f"投稿完了！Publicスコア: {public_score:.4f}")
                    else:
                        st.success(
                            f"投稿完了！Publicスコア: {public_score:.4f} / Privateスコア: {private_score:.4f}"
                        )
            except Exception as e:
                st.error(f"スコア計算または投稿処理中にエラーが発生しました: {e}")


show_submission()
