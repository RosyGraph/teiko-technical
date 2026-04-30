from typing import Literal

import pandas as pd
import streamlit as st

from loblaw.analysis import (
    compare_miraclib_pbmc_populations_by_response,
    miraclib_melanoma_pbmc_response_cell_frequencies_df,
)
from loblaw.db import SessionLocal
from loblaw.figures import (
    POPULATION_LABELS,
    all_cell_populations_boxplot,
    single_population_boxplot,
)


def __select_analysis_timepoint(
    df: pd.DataFrame,
) -> tuple[int | Literal["Analysis timepoint"], pd.DataFrame]:
    st.header("Miraclib Treatment Response")
    st.caption(
        "Analysis scope: PBMC samples from melanoma patients treated with miraclib."
    )
    timepoints = ["All timepoints"] + sorted(
        df["time_from_treatment_start"].dropna().unique().tolist()
    )
    default_timepoint, *_ = timepoints
    selected_timepoint = st.selectbox(
        "Analysis timepoint",
        timepoints,
        index=timepoints.index(default_timepoint),
    )
    if selected_timepoint == "All timepoints":
        st.warning(
            "This view pools samples across treatment timepoints. Select an individual timepoint to provide cleaner responder/non-responder comparisons when subjects have repeated samples."
        )
        analysis_df = df
    else:
        analysis_df = df[df["time_from_treatment_start"] == selected_timepoint]
    return selected_timepoint, analysis_df


def __display_response_metrics(
    analysis_df: pd.DataFrame, summary_df: pd.DataFrame
) -> None:
    c1, c2, c3, c4 = st.columns(4)
    n_responders = int(
        analysis_df[analysis_df["response"].eq(True)]["subject_id"].nunique()
    )
    n_non_responders = int(
        analysis_df[analysis_df["response"].eq(False)]["subject_id"].nunique()
    )
    c1.metric("Responder subjects", f"{n_responders:,}")
    c2.metric("Non-responder subjects", f"{n_non_responders:,}")
    c3.metric("Total subjects", f"{n_responders + n_non_responders:,}")
    c4.metric("Populations", len(summary_df))


def __response_interpretation(
    summary_df: pd.DataFrame, selected_timepoint: int | str
) -> str:
    scope_label = (
        "across all timepoints"
        if selected_timepoint == "All timepoints"
        else f"at time_from_treatment_start = {selected_timepoint}"
    )
    has_fdr_signal = summary_df["significant_bh_fdr"].any()
    best = summary_df.iloc[0]
    best_population = POPULATION_LABELS.get(best["population"], best["population"])

    if has_fdr_signal:
        return (
            f"Interpretation: {best_population} shows the strongest unadjusted difference "
            f"between responders and non-responders {scope_label}, and at least one "
            "population remains significant after BH-FDR correction."
        )
    else:
        return f"Interpretation: {best_population} shows the strongest unadjusted difference between responders and non-responders {scope_label} with an unadjusted p-value of {best['p_value']:.3f}, but no population remains significant after BH-FDR correction at 5%. Therefore, no cell population is reported as significantly different under the selected analysis scope."


def __display_statistical_summary(summary_df: pd.DataFrame) -> None:
    st.subheader("Statistical Analysis")
    st.caption(
        "Cell populations are sorted by raw p-value. BH-FDR p-values adjust across "
        "the five tested cell-population hypotheses."
    )

    st.dataframe(
        summary_df,
        hide_index=True,
        column_config={
            "n_responders": None,
            "n_non_responders": None,
            "stat": None,
            "population": "Population",
            "median_responder": "Responder median",
            "median_non_responder": "Non-responder median",
            "delta_median": "Median difference",
            "p_value": "Raw p-value",
            "p_value_bh_fdr": "BH-FDR p-value",
            "significant_raw": None,
            "significant_bh_fdr": None,
        },
    )
    st.caption(
        "Mann-Whitney U tests compare responder vs non-responder relative-frequency distributions for each cell population under the selected analysis scope. P values are shown adjusted across the five tested cell-population hypotheses using Benjamini-Hochberg FDR."
    )


def __select_population() -> str:
    st.subheader("Single Population Detail")
    default_population = "CD8 T cell"
    population_options = list(POPULATION_LABELS.values())
    return st.selectbox(
        "Cell population",
        population_options,
        index=population_options.index(default_population)
        if default_population in population_options
        else 0,
    )


with SessionLocal() as session:
    df = miraclib_melanoma_pbmc_response_cell_frequencies_df(session)

selected_timepoint, analysis_df = __select_analysis_timepoint(df)
summary_df = compare_miraclib_pbmc_populations_by_response(analysis_df)

__display_response_metrics(analysis_df, summary_df)

st.info(__response_interpretation(summary_df, selected_timepoint))

st.subheader("All Cell Populations")
st.plotly_chart(all_cell_populations_boxplot(analysis_df), width="stretch")

__display_statistical_summary(summary_df)

population = __select_population()
st.plotly_chart(single_population_boxplot(analysis_df, population), width="stretch")

with st.expander("Show underlying population-frequency rows"):
    st.dataframe(analysis_df, hide_index=True)
