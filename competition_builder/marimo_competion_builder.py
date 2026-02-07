import marimo

__generated_with = "0.19.8"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    return


@app.cell
def _():
    from drawdata import ScatterWidget
    from sklearn.model_selection import train_test_split
    import pandas as pd
    import numpy as np

    return ScatterWidget, np, pd, train_test_split


@app.cell
def _(ScatterWidget):
    widget = ScatterWidget()
    widget
    return (widget,)


@app.cell
def _(widget):
    X, y = widget.data_as_X_y
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
def _(X, pd):
    X_df = pd.DataFrame(X, columns=["feature_0"])
    X_df
    return (X_df,)


@app.cell
def _(pd, y):
    y_df = pd.DataFrame(y, columns=["target"])
    y_df
    return (y_df,)


@app.cell
def _(X_df, pd, y_df):
    data_df = pd.concat([X_df, y_df], axis=1)
    data_df
    return (data_df,)


@app.cell
def _(data_df, np, train_test_split):
    train_df, test_df = train_test_split(data_df, test_size=0.1, random_state=42, shuffle=True)
    train_df["id"] = range(len(train_df))
    test_df["id"] = range(len(train_df), len(train_df) + len(test_df))
    train_df = train_df[["id", "feature_0", "target"]]

    rng = np.random.default_rng(seed=42)

    n = len(test_df)
    usage = np.array(["Public"] * (n // 2) + ["Private"] * (n - n // 2))
    rng.shuffle(usage)

    test_df["Usage"] = usage
    test_df = test_df[["id", "feature_0", "target", "Usage"]]
    return test_df, train_df


@app.cell
def _(train_df):
    train_df
    return


@app.cell
def _(test_df):
    test_df
    return


@app.cell
def _(train_df):
    train_df.to_csv("train.csv", index=None)
    return


@app.cell
def _(test_df):
    test = test_df[["id", "feature_0"]]
    test.to_csv("test.csv", index=None)
    return


@app.cell
def _(test_df):
    ground_truth = test_df[["id", "target", "Usage"]]
    ground_truth.to_csv("ground_truth.csv", index=None)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
