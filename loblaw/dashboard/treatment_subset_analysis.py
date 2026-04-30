import pandas as pd
from loblaw.analysis import (
    load_subset_samples_by_project_df,
    load_subset_subjects_by_response_df,
    load_select_subset_subjects_by_sex_df,
)
import streamlit as st
import plotly.express as px


def display_count_bar_chart(df: pd.DataFrame, *, category: str, count: str, title: str):
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


st.title("Treatment Subset Analysis")
st.caption("Melanoma PBMC baseline samples from miraclib-treated patients.")

subset_samples_by_project_df = load_subset_samples_by_project_df()
subset_samples_by_project_df = subset_samples_by_project_df.rename(
    columns={"project": "Project", "sample_count": "Samples"}
)

subset_subjects_by_response_df = load_subset_subjects_by_response_df()
subset_subjects_by_response_df = subset_subjects_by_response_df.rename(
    columns={"response": "Response", "subject_count": "Subjects"}
)
subset_subjects_by_response_df["Response"] = subset_subjects_by_response_df[
    "Response"
].apply(lambda r: "Responder" if r else "Non-responder")

select_subset_subjects_by_sex_df = load_select_subset_subjects_by_sex_df()
select_subset_subjects_by_sex_df = select_subset_subjects_by_sex_df.rename(
    columns={"sex": "Sex", "subject_count": "Subjects"}
)

col1, col2 = st.columns(2)
col1.metric("Matching samples", int(subset_samples_by_project_df["Samples"].sum()))
col2.metric(
    "Matching subjects", int(select_subset_subjects_by_sex_df["Subjects"].sum())
)

display_count_bar_chart(
    subset_samples_by_project_df,
    category="Project",
    count="Samples",
    title="Samples by project",
)

display_count_bar_chart(
    subset_subjects_by_response_df,
    category="Response",
    count="Subjects",
    title="Subjects by response",
)

display_count_bar_chart(
    select_subset_subjects_by_sex_df,
    category="Sex",
    count="Subjects",
    title="Subjects by sex",
)

with st.expander("Show/download exact counts"):
    st.dataframe(subset_samples_by_project_df, hide_index=True)
    st.dataframe(subset_subjects_by_response_df, hide_index=True)
    st.dataframe(select_subset_subjects_by_sex_df, hide_index=True)
