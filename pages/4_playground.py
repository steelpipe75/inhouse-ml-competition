import streamlit as st
import streamlit.components.v1 as components
from st_screen_stats import ScreenData

from config import PLAYGROUND_PAGE_URL
from utils import page_config, check_password

page_config()

# 認証チェック
check_password()


def playground() -> None:
    st.title(":material/terminal: playground")

    screenD = ScreenData(setTimeout=1000)
    data = screenD.st_screen_data()

    components.iframe(
        src=PLAYGROUND_PAGE_URL,
        width=data["innerWidth"],
        height=int(data["innerHeight"] * 0.9),
    )


playground()
