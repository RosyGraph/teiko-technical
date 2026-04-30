import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

splash_page = st.Page("splash.py", title="Home", icon="🏠")
data_overview_page = st.Page("data_overview.py", title="Data Overview", icon="📊")
treatment_response_page = st.Page(
    "treatment_response.py", title="Treatment Response", icon="🧪"
)
treatment_subset_analysis_page = st.Page(
    "treatment_subset_analysis.py",
    title="Treatment Subset Analysis",
    icon="🔎",
)

pg = st.navigation(
    [
        splash_page,
        data_overview_page,
        treatment_response_page,
        treatment_subset_analysis_page,
    ]
)
pg.run()
