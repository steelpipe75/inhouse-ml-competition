# inhouse-ml-competition

機械学習コンペ運営アプリをStramlitで作成

## プロジェクト概要

このリポジトリは、内輪向けの機械学習コンペティションを運営するためのWebアプリケーションです。  
Streamlitを用いて、以下の機能を提供します。

- コンペ概要・データの公開
- 予測結果（CSVファイル）の投稿と自動スコアリング
- リーダーボードによるスコアランキング表示

## ディレクトリ構成

### 変更しないでください（アプリの構造に関わるファイル・フォルダ）

- `contents/` : Streamlitの各ページ（概要・投稿・リーダーボード）
- `streamlit_app.py` : Streamlitアプリのメインファイル
- `utils.py` : 共通関数ファイル
- `data_store.py` : データストアの抽象化モジュール

### ユーザーがカスタマイズするファイル・フォルダ

- `competition_files/data/` : 「概要・データ」で配布するファイル
- `competition_files/contents/` : 問題説明Markdown・ホーム画面Markdown
- `config.py` : コンペの設定を定義するファイル。詳細は後述。

## 設定ファイルの説明

### `config.py`
アプリの基本設定や、コンペの内容に合わせてユーザーがカスタマイズする項目を定義します。

| カテゴリ | 変数名/関数名 | 説明 |
| :--- | :--- | :--- |
| **基本設定** | `PAGE_TITLE` | アプリのタイトル |
| | `IS_COMPETITION_RUNNING` | コンペ開催中かどうかのフラグ（`True`:開催中, `False`:終了後） |
| **データストア** | `DATA_STORE_TYPE` | データストアの種類を選択 (`"google_sheet"`, `"sqlite"`, `"mysql"`, `"postgresql"`) |
| | `SPREADSHEET_NAME` | Googleスプレッドシートの名前 (`google_sheet`選択時) |
| | `LEADERBOARD_WORKSHEET_NAME`| リーダーボード用のワークシート名 (`google_sheet`選択時) |
| | `GROUND_TRUTH_WORKSHEET_NAME`| 正解データ用のワークシート名 (`google_sheet`選択時) |
| | `DB_PATH`| データベースファイルのパス (`sqlite`選択時) |
| | `LEADERBOARD_TABLE_NAME` | リーダーボードのテーブル名 (`sqlite`, `mysql`, `postgresql`選択時) |
| | `GROUND_TRUTH_TABLE_NAME` | 正解データのテーブル名 (`sqlite`, `mysql`, `postgresql`選択時) |
| **ファイルパス**| `DATA_DIR` | データファイル（学習・テスト等）を格納するディレクトリ |
| | `PROBLEM_FILE` | 問題説明Markdownファイルのパス |
| | `SAMPLE_SUBMISSION_FILE`| サンプル提出ファイルのパス |
| | `HOME_CONTENT_FILE` | Homeページのカスタマイズ用コンテンツファイルのパス |
| **リーダーボード**| `LEADERBOARD_SORT_ASCENDING`| リーダーボードのスコアソート順（`True`:昇順, `False`:降順） |
| | `LEADERBOARD_SHOW_LATEST_ONLY`| 各ユーザーの最新の投稿のみを表示するかどうか |
| **コンペ固有**| `score_submission` | public/privateスコアを計算する関数。コンペの評価指標に合わせてロジックを記述します。 |
| | `SUBMISSION_ADDITIONAL_INFO`| 投稿時にユーザーから追加で収集する情報を定義します。 |
| | `LEADERBOARD_HEADER` | リーダーボード表示用のヘッダーリストを定義します。 |
| | `GROUND_TRUTH_HEADER` | 正解データのヘッダーリストを定義します。 |

## セットアップ方法

### 1. 必要なパッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. データストアの設定

本アプリケーションは、リーダーボードや正解データの保存先として、複数のデータストアに対応しています。  
`config.py` の `DATA_STORE_TYPE` で使用するデータストアを選択し、それぞれの手順に従って設定を行ってください。

- **対応データストア:**
  - `google_sheet` (デフォルト)
  - `sqlite`
  - `postgresql`
  - `mysql`

---

#### A. Google Sheets を使用する場合 (`DATA_STORE_TYPE = "google_sheet"`)

1.  **`config.py` の設定**
    - `DATA_STORE_TYPE` が `"google_sheet"` になっていることを確認します。
    - `SPREADSHEET_NAME`, `LEADERBOARD_WORKSHEET_NAME`, `GROUND_TRUTH_WORKSHEET_NAME` に、使用するGoogleスプレッドシートの情報を設定します。

2.  **Google Cloud Platform (GCP) の設定**
    - Google Cloud Consoleでプロジェクトを作成または選択します。
    - 「APIとサービス」>「ライブラリ」から「Google Sheets API」と「Google Drive API」を有効にします。
    - 「IAMと管理」>「サービスアカウント」で新しいサービスアカウントを作成し、キー（JSON形式）をダウンロードします。

3.  **`.streamlit/secrets.toml` の設定**
    - プロジェクトルートに `.streamlit` ディレクトリを作成し、その中に `secrets.toml` ファイルを置きます。
    - `.streamlit/secrets.toml.example` を参考に、ダウンロードしたJSONキーファイルの内容を `[gcp_service_account]` セクションにコピー＆ペーストします。

    ```toml
    # .streamlit/secrets.toml

    [gcp_service_account]
    type = "service_account"
    project_id = "your-project-id"
    private_key_id = "your-private-key-id"
    private_key = "-----BEGIN PRIVATE KEY-----\n...your-private-key...\n-----END PRIVATE KEY-----\n"
    client_email = "your-client-email"
    # ... 以下、JSONファイルの内容をコピー
    ```

4.  **Googleスプレッドシートの共有設定**
    - 使用するGoogleスプレッドシートの「共有」設定を開き、サービスアカウントのメールアドレス（`secrets.toml` の `client_email`）を「編集者」として追加します。

---

#### B. SQLite を使用する場合 (`DATA_STORE_TYPE = "sqlite"`)

1.  **`config.py` の設定**
    - `DATA_STORE_TYPE` を `"sqlite"` に変更します。
    - `DB_PATH` にデータベースファイルのパスを指定します。（例: `"db/competition.db"`）
    - `LEADERBOARD_TABLE_NAME` と `GROUND_TRUTH_TABLE_NAME` に、使用するテーブル名を設定します。

SQLiteを使用する場合、`.streamlit/secrets.toml` での追加設定は不要です。
指定したパスにデータベースファイルが自動的に作成されます。

---

#### C. PostgreSQL / MySQL を使用する場合

1.  **`config.py` の設定**
    - `DATA_STORE_TYPE` を `"postgresql"` または `"mysql"` に変更します。
    - `LEADERBOARD_TABLE_NAME` と `GROUND_TRUTH_TABLE_NAME` に、使用するテーブル名を設定します。

2.  **`.streamlit/secrets.toml` の設定**
    - `.streamlit/secrets.toml.example` を参考に、データベースの接続情報を `secrets.toml` に記述します。
    - データベースの種類に応じて、`[connections.postgresql]` または `[connections.mysql]` セクションを作成し、認証情報を設定してください。

    **PostgreSQL の例:**
    ```toml
    # .streamlit/secrets.toml

    [connections.postgresql]
    dialect = "postgresql"
    driver = "psycopg2"
    username = "your_user"
    password = "your_password"
    host = "your_host"
    port = 5432
    database = "your_database"
    # url = "postgresql+psycopg2://user:pass@host:port/dbname" # もしくはURLを直接指定
    ```

    **MySQL の例:**
    ```toml
    # .streamlit/secrets.toml

    [connections.mysql]
    dialect = "mysql"
    driver = "mysqlconnector"
    username = "your_user"
    password = "your_password"
    host = "your_host"
    port = 3306
    database = "your_database"
    # url = "mysql+mysqlconnector://user:pass@host:port/dbname" # もしくはURLを直接指定
    ```
事前にデータベースとテーブルを作成しておく必要があります。

### 3. 認証の設定 (任意)

アプリケーションにアクセス制限をかけることができます。

#### パスワード保護

`config.py` の `AUTH` を `False` に設定した場合、単純なパスワード保護を利用できます。
以下のコマンドでパスワードのハッシュ値を生成し、`.streamlit/secrets.toml` の `APP_PASSWORD_HASH` に設定してください。

```bash
python scripts/generate_password_hash.py
```

```toml
# .streamlit/secrets.toml
APP_PASSWORD_HASH = "生成されたハッシュ値"
EMAIL_HASH_SALT = "your_email_hash_salt_string_here"
```
`EMAIL_HASH_SALT` には、リーダーボードでメールアドレスを匿名化するための任意の文字列を設定します。

#### OIDC認証

`config.py` の `AUTH` を `True` に設定した場合、OIDCによる認証を利用できます。
`.streamlit/secrets.toml` にOIDCプロバイダーの情報を設定してください。

```toml
# .streamlit/secrets.toml
AUTH = true
EMAIL_HASH_SALT = "your_email_hash_salt_string_here"

[auth]
redirect_uri = "your-redirect-uri"
cookie_secret = "your-cookie-secret"
client_id = "your-client-id"
client_secret = "your-client-secret"
server_metadata_url = "your-server-metadata-url"
```

### 4. アプリの起動

```bash
streamlit run streamlit_app.py
```

## 使い方

- サイドバーから「概要・データ」「投稿」「リーダーボード」ページに移動できます。
- 投稿ページでユーザー名と予測CSVをアップロードすると、自動でスコア計算・リーダーボード反映されます。

## ライセンス

MIT License
