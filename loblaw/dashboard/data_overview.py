import streamlit as st

from loblaw.analysis import load_cell_count_summary_df

st.markdown("""
# Data Overview

Each row represents one immune cell population within one sample,
including total sample count and relative frequency percentage.
""")
df = load_cell_count_summary_df()
col1, col2, col3 = st.columns(3)
col1.metric("Rows", f"{len(df):,}")
col2.metric("Samples", f"{df['sample'].nunique():,}")
col3.metric("Populations", f"{df['population'].nunique():,}")
st.dataframe(df, width="stretch")
