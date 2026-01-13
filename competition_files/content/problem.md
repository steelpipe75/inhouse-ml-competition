# タスク概要

このページはカスタマイズ可能です。

- この内容は `competition_files/content/problem.md` を編集することで変更できます。

---


## 予測タスクの説明

本コンペティションでは、与えられた特徴量 `a`, `b`, `c` から目的変数 `target` を予測します。

- 入力：
  - `id`, `a`, `b`, `c` からなるテストデータ（`test.csv`）
- 出力：
  - 各 `id` に対する予測値 `target`（`sample_submission.csv` 形式）
- 評価指標：
  - MAE（Mean Absolute Error）
