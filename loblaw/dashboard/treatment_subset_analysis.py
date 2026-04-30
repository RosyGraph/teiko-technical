from dataclasses import astuple, dataclass

import pandas as pd
import plotly.express as px
import streamlit as st

from loblaw.analysis import (
    baseline_miraclib_melanoma_pbmc_samples_by_project_df,
    baseline_miraclib_melanoma_pbmc_subjects_by_response_df,
    baseline_miraclib_melanoma_pbmc_subjects_by_sex_df,
    load_baseline_subset_tables,
)
from loblaw.db import SessionLocal
from loblaw.figures import count_bar_chart_fig

tables = load_baseline_subset_tables()

st.title("Treatment Subset Analysis")
st.caption("Melanoma PBMC baseline samples from miraclib-treated patients.")

col1, col2 = st.columns(2)
col1.metric("Matching samples", int(tables.samples_by_project["Samples"].sum()))
col2.metric("Matching subjects", int(tables.subjects_by_sex["Subjects"].sum()))

st.plotly_chart(
    count_bar_chart_fig(
        tables.samples_by_project,
        category="Project",
        count="Samples",
        title="Samples by project",
    ),
    width="stretch",
)

st.plotly_chart(
    count_bar_chart_fig(
        tables.subjects_by_response,
        category="Response",
        count="Subjects",
        title="Subjects by response",
    ),
    width="stretch",
)

st.plotly_chart(
    count_bar_chart_fig(
        tables.subjects_by_sex,
        category="Sex",
        count="Subjects",
        title="Subjects by sex",
    ),
    width="stretch",
)

with st.expander("Show/download exact counts"):
    for table in astuple(tables):
        st.dataframe(table)
