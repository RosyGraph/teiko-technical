from dataclasses import astuple, dataclass

import pandas as pd
import plotly.express as px
import streamlit as st

from loblaw.analysis import (
    baseline_miraclib_melanoma_pbmc_samples_by_project_df,
    baseline_miraclib_melanoma_pbmc_subjects_by_response_df,
    baseline_miraclib_melanoma_pbmc_subjects_by_sex_df,
)
from loblaw.db import SessionLocal


def __display_count_bar_chart(
    df: pd.DataFrame, *, category: str, count: str, title: str
):
    fig = px.bar(
        df,
        x=count,
        y=category,
        color=category,
        orientation="h",
        text=count,
        title=title,
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
    )

    fig.update_yaxes(categoryorder="total ascending")

    st.plotly_chart(fig, use_container_width=True)


@dataclass(frozen=True)
class BaselineSubsetTables:
    samples_by_project: pd.DataFrame
    subjects_by_response: pd.DataFrame
    subjects_by_sex: pd.DataFrame


def load_baseline_subset_tables() -> BaselineSubsetTables:
    with SessionLocal() as session:
        samples_by_project_df = baseline_miraclib_melanoma_pbmc_samples_by_project_df(
            session
        )
        samples_by_project_df = samples_by_project_df.rename(
            columns={"project": "Project", "sample_count": "Samples"}
        )

        subjects_by_response_df = (
            baseline_miraclib_melanoma_pbmc_subjects_by_response_df(session)
        )
        subjects_by_response_df = subjects_by_response_df.rename(
            columns={"response": "Response", "subject_count": "Subjects"}
        )
        subjects_by_response_df["Response"] = subjects_by_response_df["Response"].apply(
            lambda r: "Responder" if r else "Non-responder"
        )

        subjects_by_sex_df = baseline_miraclib_melanoma_pbmc_subjects_by_sex_df(session)
        subjects_by_sex_df = subjects_by_sex_df.rename(
            columns={"sex": "Sex", "subject_count": "Subjects"}
        )
    return BaselineSubsetTables(
        samples_by_project=samples_by_project_df,
        subjects_by_response=subjects_by_response_df,
        subjects_by_sex=subjects_by_sex_df,
    )


tables = load_baseline_subset_tables()

st.title("Treatment Subset Analysis")
st.caption("Melanoma PBMC baseline samples from miraclib-treated patients.")

col1, col2 = st.columns(2)
col1.metric("Matching samples", int(tables.samples_by_project["Samples"].sum()))
col2.metric("Matching subjects", int(tables.subjects_by_sex["Subjects"].sum()))

__display_count_bar_chart(
    tables.samples_by_project,
    category="Project",
    count="Samples",
    title="Samples by project",
)

__display_count_bar_chart(
    tables.subjects_by_response,
    category="Response",
    count="Subjects",
    title="Subjects by response",
)

__display_count_bar_chart(
    tables.subjects_by_sex,
    category="Sex",
    count="Subjects",
    title="Subjects by sex",
)

with st.expander("Show/download exact counts"):
    for table in astuple(tables):
        st.dataframe(table)
