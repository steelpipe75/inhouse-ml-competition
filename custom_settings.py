
import numpy as np
import os

# --- ユーザーが変更可能なカスタマイズ用変数 ---
DATA_DIR = "competition_files/data"      # データ（学習・テスト・サンプル提出）のディレクトリ名
PROBLEM_FILE = "competition_files/content/problem.md"     # 問題説明Markdownファイルのパス
SAMPLE_SUBMISSION_FILE = os.path.join(DATA_DIR, "sample_submission.csv")  # サンプル提出ファイルのパス
GROUND_TRUTH_FILE = "competition_files/ground_truth/ground_truth.csv"  # 正解データ（ground truth）ファイルのパス
HOME_CONTENT_FILE = "competition_files/content/home.md"   # Homeページのカスタマイズ用コンテンツファイルのパス
LEADERBOARD_SORT_ASCENDING = True        # リーダーボードのスコアソート順（True:昇順, False:降順）
IS_COMPETITION_RUNNING = True            # コンペ開催中かどうかのフラグ（True:開催中, False:終了後）

# --- スコアリング関数 ---
def score_submission(pred_df, gt_df):
    """ public/privateスコアを返す (例:MAE) """
    merged = pred_df.merge(gt_df, on="id", suffixes=("_pred", ""))

    public_mask = merged["Usage"] == "Public"
    private_mask = merged["Usage"] == "Private"

    public_score = np.mean(np.abs(merged.loc[public_mask, "target_pred"] - merged.loc[public_mask, "target"]))
    private_score = np.mean(np.abs(merged.loc[private_mask, "target_pred"] - merged.loc[private_mask, "target"]))

    return public_score, private_score
