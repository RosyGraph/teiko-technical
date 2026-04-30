from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from loblaw.analysis import (
    all_sample_cell_population_frequencies_df,
    compare_miraclib_pbmc_populations_by_response,
    miraclib_melanoma_pbmc_response_cell_frequencies_df,
)
from loblaw.db import SessionLocal
from loblaw.figures import all_cell_populations_boxplot

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


def persist_part4_baseline_miraclib_melanoma_pbmc_samples(session: Session) -> None: ...


def persist_part4_samples_by_project(session: Session) -> None: ...


def persist_part4_subjects_by_response(session: Session) -> None: ...


def persist_part4_subjects_by_sex(session: Session) -> None: ...


def persist_part4_data_subset_report(session: Session) -> None: ...


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
    persist_part4_data_subset_report(session)


def persist_all_reports(session: Session) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    persist_part2_reports(session)
    persist_part3_reports(session)
    persist_part4_reports(session)


if __name__ == "__main__":
    with SessionLocal() as session:
        persist_all_reports(session)
