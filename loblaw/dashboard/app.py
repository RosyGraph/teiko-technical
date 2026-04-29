import streamlit as st

splash_page = st.Page("splash.py", title="Home", icon="🏠")
data_overview_page = st.Page("data_overview.py", title="Data Overview", icon="📊")
treatment_response_page = st.Page(
    "treatment_response.py", title="Treatment Response", icon="🧪"
)

pg = st.navigation([splash_page, data_overview_page, treatment_response_page])
pg.run()
