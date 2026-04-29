import plotly.express as px
from loblaw.analysis import (
    load_miraclib_pbmc_cell_frequencies_df,
    compare_miraclib_pbmc_populations_by_response,
)
import streamlit as st


def display_boxplots(df):
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
        height=600,
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Single Population Detail")

    population = st.selectbox(
        "Cell population",
        sorted(df["population"].unique()),
    )

    selected = df[df["population"] == population]

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

    st.plotly_chart(detail_fig, use_container_width=True)


st.markdown("""
# Treatment Response
""")

df = load_miraclib_pbmc_cell_frequencies_df()
st.dataframe(df)

display_boxplots(df)

st.markdown("""
## Statistical Analysis
""")

summary_df = compare_miraclib_pbmc_populations_by_response(df)
c1, c2, c3, c4 = st.columns(4)
n_responders = int(summary_df.iloc[0]["n_responders"])
n_non_responders = int(summary_df.iloc[0]["n_non_responders"])
c1.metric("Responders", f"{n_responders:,}")
c2.metric("Non-responders", f"{n_non_responders:,}")
c3.metric("Total subjects", f"{n_responders + n_non_responders:,}")
c4.metric("Populations", len(summary_df))
st.dataframe(summary_df, column_config={"n_responders": None, "n_non_responders": None})
