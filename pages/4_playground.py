import streamlit as st
import streamlit.components.v1 as components

from utils import check_password
from st_screen_stats import ScreenData

# 認証チェック
check_password()


def playground() -> None:
    st.title("playground")

    screenD = ScreenData(setTimeout=1000)
    data = screenD.st_screen_data()

    components.iframe(
        "https://steelpipe75.github.io/inhouse-ml-competition-playground-sample/",
        width=data["innerWidth"],
        height=int(data["innerHeight"]*0.9),
    )


playground()
