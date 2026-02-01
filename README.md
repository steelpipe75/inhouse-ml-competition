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

### ユーザーがカスタマイズするファイル・フォルダ

- `competition_files/data/` : 「概要・データ」で配布するファイル
- `competition_files/contents/` : 問題説明Markdown・ホーム画面Markdown
- `config.py` : コンペの設定を定義するファイル。詳細は後述。

## 設定ファイルの説明

### `config.py`
アプリの基本設定や、コンペの内容に合わせてユーザーがカスタマイズする項目を定義します。

| カテゴリ | 変数名/関数名 | 説明 |
| :--- | :--- | :--- |
| **基本設定** | `PAGE_TITLE`, `PAGE_ICON` | アプリのタイトルとアイコン |
| | `IS_COMPETITION_RUNNING` | コンペ開催中かどうかのフラグ（`True`:開催中, `False`:終了後） |
| **データストア** | `DATA_STORE_TYPE` | データストアの種類を選択 (`"google_sheet"`, `"sqlite"` など) |
| | `SPREADSHEET_NAME` | Googleスプレッドシートの名前 (google_sheet選択時) |
| | `LEADERBOARD_WORKSHEET_NAME`| リーダーボード用のワークシート名 (google_sheet選択時) |
| | `GROUND_TRUTH_WORKSHEET_NAME`| 正解データ用のワークシート名 (google_sheet選択時) |
| | `DB_PATH`, `DB_URL`| データベースのパスまたはURL (sqlite, mysql, postgresql選択時) |
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

1. 必要なパッケージのインストール

```bash
pip install -r requirements.txt
```

2. アプリの起動

```bash
streamlit run streamlit_app.py
```

3. Google Sheets API設定

StreamlitアプリからGoogleスプレッドシートにアクセスするために、Google Cloud Platform (GCP) のサービスアカウント設定が必要です。

1.  **GCPでサービスアカウントを作成**
    *   Google Cloud Consoleにアクセスし、新しいプロジェクトを作成するか、既存のプロジェクトを選択します。
    *   「APIとサービス」>「ライブラリ」から「Google Sheets API」と「Google Drive API」を検索し、有効にします。
    *   「IAMと管理」>「サービスアカウント」に移動し、新しいサービスアカウントを作成します。
    *   サービスアカウント作成時に「キーを作成」を選択し、「JSON」形式でキーファイルをダウンロードします。このファイルには、スプレッドシートへのアクセスに必要な認証情報が含まれています。

2.  **.streamlit/secrets.tomlの設定**
    *   ダウンロードしたJSONキーファイルの内容を、`.streamlit/secrets.toml`ファイルに記述します。
    *   プロジェクトルートに `.streamlit` ディレクトリがない場合は作成します。
    *   `.streamlit/secrets.toml.example`を参考に、JSONキーの内容を`[gcp_service_account]`セクションにペーストします。特に`private_key`の値は、JSONファイル内の `private_key` の値をそのままコピー＆ペーストしてください（改行コードなども含めて）。

    *   **APP_PASSWORD_HASHの設定**
        アプリへのアクセスを制限したい場合、`APP_PASSWORD_HASH`を設定します。`generate_hash.py`スクリプトを使用してパスワードのハッシュ値を生成し、`.streamlit/secrets.toml`に記述してください。

        ```toml
        APP_PASSWORD_HASH = "生成されたハッシュ値"
        ```

    **secrets.tomlの例:**
    ```toml
    APP_PASSWORD_HASH = "your_sha256_hashed_password_here"
    
    [gcp_service_account]
    type = "service_account"
    project_id = "your-project-id"
    private_key_id = "your-private-key-id"
    private_key = "-----BEGIN PRIVATE KEY-----\n...your-private-key...\n-----END PRIVATE KEY-----\n" # JSONキーファイルからコピー
    client_email = "your-client-email"
    client_id = "your-client-id"
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    token_uri = "https://oauth2.googleapis.com/token"
    auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
    client_x509_cert_url = "your-client-x509-cert-url"
    universe_domain = "googleapis.com"
    ```

3.  **Googleスプレッドシートの共有設定**
    *   コンペで使用するGoogleスプレッドシートを開きます。
    *   スプレッドシートの「共有」設定を開き、サービスアカウントのメールアドレス（`client_email`の値）を「編集者」として追加します。

## 使い方

- サイドバーから「概要・データ」「投稿」「リーダーボード」ページに移動できます。
- 投稿ページでユーザー名と予測CSVをアップロードすると、自動でスコア計算・リーダーボード反映されます。

## ライセンス

MIT License
