import streamlit as st

from custom_settings import APP_NAVIGATION_PAGES

pg = st.navigation(APP_NAVIGATION_PAGES)
pg.run()
