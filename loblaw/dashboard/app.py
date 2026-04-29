import streamlit as st

splash_page = st.Page("splash.py", title="Home", icon="🏠")
data_overview_page = st.Page("data_overview.py", title="Data Overview", icon="📊")

pg = st.navigation([splash_page, data_overview_page])
pg.run()
