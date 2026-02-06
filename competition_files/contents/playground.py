import streamlit as st
import streamlit.components.v1 as components
from st_screen_stats import ScreenData

from utils import page_config, check_password

# --- Playground Page Settings ---
PLAYGROUND_PAGE_URL_JUPYTERLITE = "https://steelpipe75.github.io/inhouse-ml-competition/JupyterLite/"
PLAYGROUND_PAGE_URL_MARIMO = "https://steelpipe75.github.io/inhouse-ml-competition/marimo/"
PLAYGROUND_PAGE_URL_COLAB = "https://colab.research.google.com/github/steelpipe75/inhouse-ml-competition/blob/main/competition_files/playground/Colab/sample.ipynb"

page_config()

st.title(":material/terminal: playground")

# 認証チェック
check_password()


def playground() -> None:
    screenD = ScreenData(setTimeout=1000)
    data = screenD.st_screen_data()

    calculated_height = int(data["innerHeight"] * 0.9)
    iframe_height = max(calculated_height, 720)

    select_playground = st.segmented_control(
        "select type",
        ["JupyterLite", "marimo", "Colab"],
        selection_mode="single",
        default="JupyterLite"
    )

    if select_playground == "JupyterLite":
        components.iframe(
            src=PLAYGROUND_PAGE_URL_JUPYTERLITE,
            width=data["innerWidth"],
            height=iframe_height,
        )
        st.link_button(
            "JupyterLite サンプルスクリプトを別タブで開く",
            url=PLAYGROUND_PAGE_URL_JUPYTERLITE,
        )
    elif select_playground == "marimo":
        components.iframe(
            src=PLAYGROUND_PAGE_URL_MARIMO,
            width=data["innerWidth"],
            height=iframe_height,
        )
        st.link_button(
            "marimo サンプルスクリプトを別タブで開く",
            url=PLAYGROUND_PAGE_URL_MARIMO,
        )
    else:
        st.write("Colabのサンプルスクリプトはiframeで表示できないため、以下のリンクからColabを開いてください。")
        st.link_button(
            "Colab サンプルスクリプトを別タブで開く",
            url=PLAYGROUND_PAGE_URL_COLAB,
        )


playground()
