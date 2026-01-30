import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import hashlib
import os

# データ生成の設定
SALT = "gemini-cli-test-salt"
OUTPUT_DIR = "dev_data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "test_leaderboard_data.csv")

JST = ZoneInfo("Asia/Tokyo")

def generate_hash(username: str) -> str:
    """ユーザー名から決定的なハッシュ値を生成する"""
    return hashlib.sha256(f"{username}{SALT}".encode()).hexdigest()

# --- ユーザーごとの投稿内容を定義 ---
users_data = {
    "user_a": [
        {"days": 4, "hours": 2, "public": 0.18532, "private": 0.19987, "comment": "first try"},
        {"days": 3, "hours": 1, "public": 0.11543, "private": 0.13876, "comment": "tuned parameters"}
    ],
    "user_b": [
        {"days": 5, "hours": 0, "public": 0.09112, "private": 0.25432, "comment": "overfitted model?"}
    ],
    "user_c": [
        {"days": 2, "hours": 12, "public": 0.22456, "private": 0.10187, "comment": "robust model"}
    ],
    "user_d": [
        {"days": 6, "hours": 0, "public": 0.30123, "private": 0.31234, "comment": "baseline"},
        {"days": 4, "hours": 8, "public": 0.20876, "private": 0.24987, "comment": "feature engineering"},
        {"days": 1, "hours": 5, "public": 0.18998, "private": 0.19555, "comment": "final submission"}
    ],
    "user_e": [
        {"days": 2, "hours": 3, "public": 0.15678, "private": 0.16234, "comment": "new idea"}
    ]
}

# --- データレコードを生成 ---
data = []
now = datetime.now(JST)
for username, submissions in users_data.items():
    for sub in submissions:
        data.append({
            "username": username,
            "email_hash": generate_hash(username),
            "public_score": sub["public"],
            "private_score": sub["private"],
            "submission_time": (now - timedelta(days=sub["days"], hours=sub["hours"])).strftime("%Y-%m-%d %H:%M:%S%z"),
            "comment": sub["comment"],
        })

# DataFrameに変換
df = pd.DataFrame(data)

# ヘッダーの順番を custom_settings.py に合わせる
header = [
    "username", "email_hash", "public_score", "private_score",
    "submission_time", "comment",
]
df = df[header]

# CSVファイルに直接書き込む
# lineterminator='\n' を指定して、改行コードをLFに統一する
df.to_csv(OUTPUT_FILE, index=False, lineterminator='\n')

print(f"CSV file '{OUTPUT_FILE}' has been generated successfully.")