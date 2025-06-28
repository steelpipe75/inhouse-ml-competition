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

- `pages/` : Streamlitの各ページ（概要・投稿・リーダーボード）
- `submissions/` : 投稿された予測ファイル（自動生成）
- `leaderboard/` : リーダーボードCSV（自動生成）
- `config.py` : 設定ファイル（基本設定）
- `Home.py` : Streamlitアプリのメインファイル

### ユーザーがカスタマイズするファイル・フォルダ

- `competition_files/data/` : 「概要・データ」で配布するファイル
- `competition_files/ground_truth/` : 正解データ
- `competition_files/content/` : 問題説明Markdown・ホーム画面Markdown
- `custom_settings.py` : ユーザーが編集する設定ファイル

## 設定ファイル（custom_settings.py）の説明

`custom_settings.py` には、ユーザーがカスタマイズ可能な各種パスや設定値、スコア計算関数が定義されています。

| 変数名                        | 説明                                                                    |
|------------------------------|------------------------------------------------------------------------|
| `DATA_DIR`                   | データファイル（「概要・データ」ページで配布するファイル）のディレクトリ名<br>例: `competition_files/data` |
| `PROBLEM_FILE`               | 問題説明Markdownファイルのパス<br>例: `competition_files/content/problem.md` |
| `SAMPLE_SUBMISSION_FILE`     | サンプル提出ファイルのパス<br>例: `competition_files/data/sample_submission.csv` |
| `GROUND_TRUTH_FILE`          | 正解データ（ground truth）ファイルのパス<br>例: `competition_files/ground_truth/ground_truth.csv` |
| `LEADERBOARD_SORT_ASCENDING` | リーダーボードのスコアソート順（True:昇順, False:降順）                     |
| `IS_COMPETITION_RUNNING`     | コンペ開催中かどうかのフラグ（True:開催中, False:終了後）                   |
| `score_submission`           | 提出ファイルと正解データを比較し、public/privateスコアを返す関数（例: MAE）  |

## セットアップ方法

1. 必要なパッケージのインストール

```bash
pip install -r requirements.txt
```

2. アプリの起動

```bash
streamlit run Home.py
```

## 使い方

- サイドバーから「概要・データ」「投稿」「リーダーボード」ページに移動できます。
- 投稿ページでユーザー名と予測CSVをアップロードすると、自動でスコア計算・リーダーボード反映されます。

## ライセンス

MIT License
