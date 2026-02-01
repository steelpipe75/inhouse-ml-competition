import streamlit as st

from config import APP_NAVIGATION_PAGES

pg = st.navigation(APP_NAVIGATION_PAGES)
pg.run()
