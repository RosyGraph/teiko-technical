import plotly.express as px
from loblaw.analysis import load_miraclib_pbmc_cell_frequencies_df
import streamlit as st

st.markdown("""
# Treatment Response
""")

df = load_miraclib_pbmc_cell_frequencies_df()
st.dataframe(df)
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
