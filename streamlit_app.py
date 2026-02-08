import streamlit as st

from config import get_APP_NAVIGATION_PAGES

pg = st.navigation(get_APP_NAVIGATION_PAGES())
pg.run()
