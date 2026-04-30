import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure

POPULATION_LABELS = {
    "b_cell": "B cell",
    "cd4_t_cell": "CD4 T cell",
    "cd8_t_cell": "CD8 T cell",
    "monocyte": "Monocyte",
    "nk_cell": "NK cell",
}


def all_cell_populations_boxplot(df: pd.DataFrame) -> Figure:
    df = df.copy()
    df["response_label"] = df["response"].map(
        {
            True: "Responder",
            False: "Non-responder",
        }
    )

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
    return fig


def single_population_boxplot(df: pd.DataFrame, population: str) -> Figure:
    df = df.copy()

    df["response_label"] = df["response"].map(
        {
            True: "Responder",
            False: "Non-responder",
        }
    )
    df["population_label"] = df["population"].map(POPULATION_LABELS)
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
    return detail_fig
