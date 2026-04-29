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


st.markdown("""
# Treatment Response
""")
df = load_miraclib_pbmc_cell_frequencies_df()
summary_df = compare_miraclib_pbmc_populations_by_response(df)
c1, c2, c3, c4 = st.columns(4)
n_responders = int(summary_df.iloc[0]["n_responders"])
n_non_responders = int(summary_df.iloc[0]["n_non_responders"])
c1.metric("Responders", f"{n_responders:,}")
c2.metric("Non-responders", f"{n_non_responders:,}")
c3.metric("Total subjects", f"{n_responders + n_non_responders:,}")
c4.metric("Populations", len(summary_df))
display_all_cell_boxplot(df)
st.subheader("Statistical Analysis")
st.markdown("""
CD4 T cells show the strongest unadjusted difference between responders and non-responders, but no cell population remained significant after BH-FDR correction at 5%.
""")

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
    "Mann-Whitney U tests compare responder vs non-repsonder distributions for each cell population. P values are shown adjusted across the five tested cell-population hypotheses using Benjamini-Hochberg FDR."
)

display_single_population_boxplots(df)

st.dataframe(df)
