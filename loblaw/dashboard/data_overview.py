import streamlit as st

from loblaw.analysis import (
    all_sample_cell_population_frequencies_df,
    miraclib_melanoma_pbmc_response_cell_frequencies_df,
)
from loblaw.db import SessionLocal

st.markdown("""
# Data Overview

Each row represents one immune cell population within one sample,
including total sample count and relative frequency percentage.
""")
with SessionLocal() as session:
    df = all_sample_cell_population_frequencies_df(session)
col1, col2, col3 = st.columns(3)
col1.metric("Rows", f"{len(df):,}")
col2.metric("Samples", f"{df['sample'].nunique():,}")
col3.metric("Populations", f"{df['population'].nunique():,}")
st.dataframe(df, width="stretch")
