import streamlit as st

# --- Google Sheets Settings ---
SPREADSHEET_NAME = "sample_spreadsheets"  # ここにスプレッドシート名を入力してください
LEADERBOARD_WORKSHEET_NAME = "leaderboard"  # リーダーボード用のワークシート名
GROUND_TRUTH_WORKSHEET_NAME = "ground_truth"  # 正解データ用のワークシート名

# --- Playground Page Settings ---
PLAYGROUND_PAGE_URL = "https://steelpipe75.github.io/inhouse-ml-competition-playground-sample/"  # PlaygroundページのURL

# --- Competition Settings ---
IS_COMPETITION_RUNNING = (
    False  # コンペ開催中かどうかのフラグ（True:開催中, False:終了後）
)

# --- Password Protection Settings ---
PROTECT_ALL_PAGES = False  # Trueの場合、すべてのページを保護します。Falseの場合、投稿とリーダーボードページのみを保護します。

# --- Page Settings ---
PAGE_TITLE = "内輪向け機械学習コンペアプリ"
PAGE_ICON = "🏆"

# --- Auth ---
try:
    AUTH = st.secrets["AUTH"]
except (KeyError, FileNotFoundError):
    AUTH = False

# --- Email Hash Salt ---
if AUTH:
    try:
        EMAIL_HASH_SALT: str = st.secrets["EMAIL_HASH_SALT"]
    except KeyError:
        raise RuntimeError(
            "st.secrets に 'EMAIL_HASH_SALT' が設定されていません。ハッシュ化にはsaltが必要です。"
        )
else:
    EMAIL_HASH_SALT = ""


# --- Data Store Settings ---
# データストアの種類を選択: "google_sheet", "sqlite", "mysql", "postgresql"
DATA_STORE_TYPE = "google_sheet"

# --- For SQLite ---
DB_PATH = "db/competition.db"

# --- For MySQL/PostgreSQL ---
# 例: "mysql+mysqlconnector://user:password@host:port/database"
# 例: "postgresql+psycopg2://user:password@host:port/database"
DB_URL = ""

# --- For Database Table Names ---
LEADERBOARD_TABLE_NAME = "leaderboard"
GROUND_TRUTH_TABLE_NAME = "ground_truth"
