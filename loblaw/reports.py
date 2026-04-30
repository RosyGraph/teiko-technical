from pathlib import Path

import pandas as pd
from plotly.graph_objects import Figure
from sqlalchemy.orm import Session

from loblaw.analysis import (
    all_sample_cell_population_frequencies_df,
    baseline_miraclib_melanoma_pbmc_samples_by_project_df,
    baseline_miraclib_melanoma_pbmc_samples_df,
    baseline_miraclib_melanoma_pbmc_subjects_by_response_df,
    baseline_miraclib_melanoma_pbmc_subjects_by_sex_df,
    calculate_avg_b_cells_for_baseline_responders,
    compare_miraclib_pbmc_populations_by_response,
    miraclib_melanoma_pbmc_response_cell_frequencies_df,
)
from loblaw.db import SessionLocal
from loblaw.figures import all_cell_populations_boxplot, count_bar_chart_fig
from loblaw.logging_config import configure_logging

REPORTS_DIR = Path("reports/")


def persist_part2_all_cell_population_frequencies(session: Session) -> None:
    df = all_sample_cell_population_frequencies_df(session)
    df.to_csv(REPORTS_DIR / "part2_all_cell_population_frequencies.csv", index=False)


def persist_part2_metadata(session: Session) -> None:
    df = all_sample_cell_population_frequencies_df(session)

    metadata = pd.DataFrame(
        [
            {"metric": "rows", "value": len(df)},
            {"metric": "samples", "value": df["sample"].nunique()},
            {"metric": "populations", "value": df["population"].nunique()},
        ]
    )
    metadata.to_csv(REPORTS_DIR / "part2_metadata.csv", index=False)


def persist_part3_miraclib_pbmc_response_cell_frequencies(
    session: Session,
) -> None:
    df = miraclib_melanoma_pbmc_response_cell_frequencies_df(session)
    df.to_csv(
        REPORTS_DIR / "part3_miraclib_pbmc_response_cell_frequencies.csv", index=False
    )


def persist_part3_population_response_statistics(
    session: Session,
) -> None:
    df = miraclib_melanoma_pbmc_response_cell_frequencies_df(session)
    summary_df = compare_miraclib_pbmc_populations_by_response(df)
    summary_df.to_csv(
        REPORTS_DIR / "part3_population_response_statistics.csv", index=False
    )


def persist_part3_all_cell_populations_boxplot(
    session: Session,
) -> None:
    df = miraclib_melanoma_pbmc_response_cell_frequencies_df(session)
    fig = all_cell_populations_boxplot(df)
    fig.write_html(REPORTS_DIR / "part3_all_cell_populations_boxplot.html")


def persist_part4_baseline_miraclib_melanoma_pbmc_samples(session: Session) -> None:
    df = baseline_miraclib_melanoma_pbmc_samples_df(session)
    df.to_csv(
        REPORTS_DIR / "part4_baseline_miraclib_melanoma_pbmc_samples.csv", index=False
    )


def __persist_part4_df_and_figure(df: pd.DataFrame, fig: Figure, stem: str):
    df.to_csv(REPORTS_DIR / f"{stem}.csv", index=False)
    fig.write_html(REPORTS_DIR / f"{stem}.html")


def persist_part4_samples_by_project(session: Session) -> None:
    df = baseline_miraclib_melanoma_pbmc_samples_by_project_df(session)
    fig = count_bar_chart_fig(
        df,
        category="project",
        count="sample_count",
        title="Samples by project",
    )
    __persist_part4_df_and_figure(df, fig, "part4_samples_by_project")


def persist_part4_subjects_by_response(session: Session) -> None:
    df = baseline_miraclib_melanoma_pbmc_subjects_by_response_df(session)
    fig = count_bar_chart_fig(
        df,
        category="response",
        count="subject_count",
        title="Subjects by response",
    )
    __persist_part4_df_and_figure(df, fig, "part4_subjects_by_response")


def persist_part4_subjects_by_sex(session: Session) -> None:
    df = baseline_miraclib_melanoma_pbmc_subjects_by_sex_df(session)
    fig = count_bar_chart_fig(
        df,
        category="sex",
        count="subject_count",
        title="Subjects by sex",
    )
    __persist_part4_df_and_figure(df, fig, "part4_subjects_by_sex")


def persist_part2_reports(session: Session) -> None:
    persist_part2_all_cell_population_frequencies(session)
    persist_part2_metadata(session)


def persist_part3_reports(
    session: Session,
) -> None:
    persist_part3_miraclib_pbmc_response_cell_frequencies(session)
    persist_part3_population_response_statistics(session)
    persist_part3_all_cell_populations_boxplot(session)


def persist_part4_reports(session: Session) -> None:
    persist_part4_baseline_miraclib_melanoma_pbmc_samples(session)
    persist_part4_samples_by_project(session)
    persist_part4_subjects_by_response(session)
    persist_part4_subjects_by_sex(session)


def persist_melanoma_male_responder_baseline_b_cell_average(session: Session) -> None:
    value = calculate_avg_b_cells_for_baseline_responders(session)
    (REPORTS_DIR / "melanoma_male_responder_baseline_b_cell_average.txt").write_text(
        str(value)
    )


def persist_all_reports(session: Session) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    persist_part2_reports(session)
    persist_part3_reports(session)
    persist_part4_reports(session)
    persist_melanoma_male_responder_baseline_b_cell_average(session)


if __name__ == "__main__":
    configure_logging()
    with SessionLocal() as session:
        persist_all_reports(session)
