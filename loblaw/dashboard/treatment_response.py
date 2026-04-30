import plotly.express as px
from loblaw.analysis import (
    load_miraclib_pbmc_cell_frequencies_df,
    compare_miraclib_pbmc_populations_by_response,
)
import streamlit as st

POPULATION_LABELS = {
    "b_cell": "B cell",
    "cd4_t_cell": "CD4 T cell",
    "cd8_t_cell": "CD8 T cell",
    "monocyte": "Monocyte",
    "nk_cell": "NK cell",
}


def display_all_cell_boxplot(df):
    df = df.copy()
    df["response_label"] = df["response"].map(
        {
            True: "Responder",
            False: "Non-responder",
        }
    )

    st.subheader("All Cell Populations")

    fig = px.box(
        df,
        x="population",
        y="percentage",
        color="response_label",
        points="outliers",
        labels={
            "population": "Cell Population",
            "percentage": "Relative Frequency (%)",
            "response_label": "Response",
        },
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        boxmode="group",
    )

    st.plotly_chart(fig, width="stretch")


def display_single_population_boxplots(df):
    df = df.copy()

    df["response_label"] = df["response"].map(
        {
            True: "Responder",
            False: "Non-responder",
        }
    )
    df["population_label"] = df["population"].map(POPULATION_LABELS)
    st.subheader("Single Population Detail")
    population = st.selectbox(
        "Cell population",
        sorted(df["population_label"].unique()),
        index=sorted(df["population_label"].unique()).index("CD4 T cell"),
    )
    selected = df[df["population_label"] == population]
    detail_fig = px.box(
        selected,
        x="response_label",
        y="percentage",
        points="all",
        labels={
            "response_label": "Response",
            "percentage": "Relative Frequency (%)",
        },
        title=f"{population}: Responders vs Non-responders",
    )

    st.plotly_chart(detail_fig, width="stretch")


st.header("Miraclib Treatment Response")
st.caption("Analysis scope: PBMC samples from melanoma patients treated with miraclib.")
df = load_miraclib_pbmc_cell_frequencies_df()
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
summary_df = compare_miraclib_pbmc_populations_by_response(analysis_df)
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
scope_label = (
    "across all timepoints"
    if selected_timepoint == "All timepoints"
    else f"at time_from_treatment_start = {selected_timepoint}"
)

has_fdr_signal = summary_df["significant_bh_fdr"].any()
has_raw_signal = summary_df["significant_raw"].any()
best = summary_df.iloc[0]
best_population = POPULATION_LABELS.get(best["population"], best["population"])

if has_fdr_signal:
    st.info(
        f"Interpretation: {best_population} shows the strongest unadjusted difference "
        f"between responders and non-responders {scope_label}, and at least one "
        "population remains significant after BH-FDR correction."
    )
else:
    st.info(
        f"Interpretation: {best_population} shows the strongest unadjusted difference between responders and non-responders {scope_label} with an unadjusted p-value of {best['p_value']:.3f}, but no population remains significant after BH-FDR correction at 5%. Therefore, no cell population is reported as significantly different under the selected analysis scope."
    )
display_all_cell_boxplot(analysis_df)
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

display_single_population_boxplots(analysis_df)

with st.expander("Show underlying population-frequency rows"):
    st.dataframe(analysis_df, hide_index=True)
