import streamlit as st

pg = st.navigation(
    [
        st.Page("contents/home.py", title="Home", icon=":material/home:"),
        st.Page(
            "contents/problem.py", title="概要・データ", icon=":material/menu_book:"
        ),
        st.Page("contents/submit.py", title="予測結果の投稿", icon=":material/send:"),
        st.Page(
            "contents/leaderboard.py",
            title="リーダーボード",
            icon=":material/leaderboard:",
        ),
        st.Page(
            "contents/playground.py", title="playground", icon=":material/terminal:"
        ),
    ]
)
pg.run()
