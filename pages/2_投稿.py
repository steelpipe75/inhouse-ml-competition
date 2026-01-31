import streamlit as st
import pandas as pd
import datetime
import hashlib
from typing import Dict
from zoneinfo import ZoneInfo

from custom_settings import (
    SAMPLE_SUBMISSION_FILE,
    SUBMISSION_ADDITIONAL_INFO,
    score_submission,
    read_ground_truth,
    write_submission,
)
from config import (
    IS_COMPETITION_RUNNING,
    AUTH,
    EMAIL_HASH_SALT,
)
from utils import page_config, check_password
from data_store import get_data_store

JST = ZoneInfo("Asia/Tokyo")

page_config()

# 認証チェック
check_password(always_protect=True)


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
    st.title(":material/send: 予測結果の投稿")
    username = st.text_input("ユーザー名", icon=":material/person:")

    # 追加の入力欄を動的に生成
    additional_inputs = render_additional_inputs()

    uploaded_file = st.file_uploader("予測CSVをアップロード", type="csv")

    if st.button("投稿する", icon=":material/send:"):
        if AUTH:
            email = st.user.email
        else:
            email = "None"
        if not username:
            st.error("ユーザー名を入力してください。")
        elif not email:
            st.error("ログインしていません。ログインしてください。")
        elif not uploaded_file:
            st.error("CSVファイルをアップロードしてください。")
        else:
            # ground_truthが設定されているかチェック
            if not get_data_store().has_ground_truth():
                st.error(
                    "正解データが登録されていません。管理者に連絡いただくか、正解データを登録してください。"
                )
                return  # ここで処理を中断
            with st.spinner("投稿を処理中..."):
                try:
                    submission_df = pd.read_csv(uploaded_file)
                    sample_df = pd.read_csv(SAMPLE_SUBMISSION_FILE)
                    ground_truth_df = read_ground_truth()

                    if list(submission_df.columns) != list(sample_df.columns):
                        st.error("カラムが期待する形と一致していません。")
                    elif len(submission_df) != len(sample_df):
                        st.error("行数が期待する形と一致していません。")
                    else:
                        public_score, private_score = score_submission(
                            submission_df, ground_truth_df
                        )

                        # emailをハッシュ化 (saltを使用)
                        if AUTH:
                            email_hash = hashlib.sha256(
                                (email + EMAIL_HASH_SALT).encode()
                            ).hexdigest()
                        else:
                            email_hash = ""

                        # 投稿データを作成
                        submission_data = {
                            "username": username,
                            "public_score": public_score,
                            "private_score": private_score,
                            "submission_time": datetime.datetime.now(JST).strftime(
                                "%Y-%m-%d %H:%M:%S%z"
                            ),
                        }
                        submission_data.update(additional_inputs)
                        if AUTH:
                            submission_data.update({"email_hash": email_hash})

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
