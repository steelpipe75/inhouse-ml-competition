# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.19.0",
#     "matplotlib==3.10.8",
#     "numpy==2.4.2",
#     "polars==1.38.1",
#     "pyzmq>=27.1.0",
#     "scikit-learn==1.8.0",
# ]
# ///

import marimo

__generated_with = "0.19.9"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 機械学習コンペ サンプルノートブック
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## WASM環境であればpolarsをインストール
    """)
    return


@app.cell
def _():
    import sys

    return (sys,)


@app.cell
def _(sys):
    IS_WASM = sys.platform == "emscripten"
    return (IS_WASM,)


@app.cell
def _(IS_WASM):
    if IS_WASM:
        import micropip
    return (micropip,)


@app.cell
async def _(IS_WASM, micropip):
    if IS_WASM:
        await micropip.install("polars")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ライブラリをインポート
    """)
    return


@app.cell
def _():
    import polars as pl
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression as LR
    from matplotlib import pyplot as plt
    from sklearn.metrics import mean_squared_error as MSE

    return LR, np, pl, plt, train_test_split


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## コンペ配布データ読み込み
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 学習用データ読み込み
    """)
    return


@app.cell
def _(mo):
    train_csv_path = mo.notebook_location() / "public" / "data" / "train.csv"
    train_csv_path
    return (train_csv_path,)


@app.cell
def _(pl, train_csv_path):
    train_df = pl.read_csv(str(train_csv_path))
    train_df
    return (train_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 評価用データ読み込み
    """)
    return


@app.cell
def _(mo):
    test_csv_path = mo.notebook_location() / "public" / "data" / "test.csv"
    test_csv_path
    return (test_csv_path,)


@app.cell
def _(pl, test_csv_path):
    test_df = pl.read_csv(str(test_csv_path))
    test_df
    return (test_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### サンプル投稿ファイル読み込み
    """)
    return


@app.cell
def _(mo):
    submit_csv_path = (
        mo.notebook_location() / "public" / "data" / "sample_submission.csv"
    )
    submit_csv_path
    return (submit_csv_path,)


@app.cell
def _(pl, submit_csv_path):
    submit = pl.read_csv(str(submit_csv_path))
    submit
    return (submit,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 前処理
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 説明変数、目的変数に分割
    """)
    return


@app.cell
def _(train_df):
    X = train_df[["a", "b"]]
    y = train_df["c"]
    return X, y


@app.cell
def _(X):
    X
    return


@app.cell
def _(y):
    y
    return


@app.cell
def _(test_df):
    X_test = test_df[["a", "b"]]
    return (X_test,)


@app.cell
def _(X_test):
    X_test
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 訓練用データ、検証用データに分割
    """)
    return


@app.cell
def _(X, train_test_split, y):
    X_train, X_eval, y_train, y_eval = train_test_split(X, y)
    return X_eval, X_train, y_eval, y_train


@app.cell
def _(X_train):
    X_train
    return


@app.cell
def _(y_train):
    y_train
    return


@app.cell
def _(X_eval):
    X_eval
    return


@app.cell
def _(y_eval):
    y_eval
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## モデルを訓練
    """)
    return


@app.cell
def _(LR):
    model = LR()
    return (model,)


@app.cell
def _(X_train, model, y_train):
    model.fit(X_train, y_train)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 訓練済みモデルによる予測（検証用データ）
    """)
    return


@app.cell
def _(X_eval, model):
    y_pred_eval = model.predict(X_eval)
    return (y_pred_eval,)


@app.cell
def _(y_pred_eval):
    y_pred_eval
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    予測精度の可視化
    """)
    return


@app.cell
def _(np, plt, y_eval, y_pred_eval):
    plt.scatter(y_eval, y_pred_eval)

    y_eval_min = np.min(y_eval.to_numpy())
    y_eval_max = np.max(y_eval.to_numpy())
    y_pred_eval_min = np.min(y_pred_eval)
    y_pred_eval_max = np.max(y_pred_eval)
    y_min = np.minimum(y_eval_min, y_pred_eval_min)
    y_max = np.maximum(y_eval_max, y_pred_eval_max)

    y_range = y_max - y_min

    lim_min = y_min - (y_range * 0.1)
    lim_max = y_max + (y_range * 0.1)

    plt.xlim([lim_min, lim_max])
    plt.ylim([lim_min, lim_max])

    plt.plot([lim_min, lim_max], [lim_min, lim_max])

    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 訓練済みモデルによる予測（評価用データ）
    """)
    return


@app.cell
def _(X_test, model):
    y_pred_test = model.predict(X_test)
    return (y_pred_test,)


@app.cell
def _(y_pred_test):
    y_pred_test
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 採点用投稿ファイル作成
    """)
    return


@app.cell
def _(pl, submit, y_pred_test):
    my_submit = submit.with_columns(pl.Series("target", y_pred_test))
    return (my_submit,)


@app.cell
def _(my_submit):
    my_submit
    return


@app.cell
def _(my_submit):
    my_submit.write_csv("submit.csv")
    return


if __name__ == "__main__":
    app.run()
