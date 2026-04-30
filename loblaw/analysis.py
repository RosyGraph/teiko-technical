import logging
from collections.abc import Mapping, Sequence
from csv import DictWriter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats.mstats import mannwhitneyu
from sqlalchemy import RowMapping, Select, func, select
from sqlalchemy.orm import Session

from loblaw.db import SessionLocal
from loblaw.models import CellCount, Project, Sample, Subject
from loblaw.queries import (
    all_sample_cell_population_frequencies_stmt,
    baseline_miraclib_melanoma_pbmc_samples_by_project_stmt,
    baseline_miraclib_melanoma_pbmc_subjects_by_response_stmt,
    baseline_miraclib_melanoma_pbmc_subjects_by_sex_stmt,
    miraclib_melanoma_pbmc_response_cell_frequencies_stmt,
)

DEFAULT_CELL_COUNT_SUMMARY_PATH = Path("reports/cell_counts_summary.csv")
logger = logging.getLogger(__name__)


def miraclib_melanoma_pbmc_response_cell_frequencies_df(
    session: Session,
) -> pd.DataFrame:
    stmt = miraclib_melanoma_pbmc_response_cell_frequencies_stmt()
    return pd.read_sql(stmt, session.bind)


def bh_fdr(p_values: pd.Series) -> pd.Series:
    p = p_values.to_numpy(dtype=float)
    n = len(p)
    order = np.argsort(p)
    ranked_p = p[order]

    adjusted = ranked_p * n / np.arange(1, n + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    adjusted = np.clip(adjusted, 0, 1)
    result = np.empty_like(adjusted)
    result[order] = adjusted

    return pd.Series(result, index=p_values.index)


def compare_populations(group: pd.DataFrame) -> pd.Series:
    responders = group.loc[group["response"].eq(True), "percentage"]
    non = group.loc[group["response"].eq(False), "percentage"]
    stat, p = mannwhitneyu(responders, non)
    responders_median = responders.median()
    non_median = non.median()
    return pd.Series(
        {
            "n_responders": len(responders),
            "n_non_responders": len(non),
            "median_responder": responders_median,
            "median_non_responder": non_median,
            "delta_median": responders_median - non_median,
            "p_value": p,
            "stat": stat,
        }
    )


def compare_miraclib_pbmc_populations_by_response(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df_with_p_values = df.groupby("population").apply(compare_populations).reset_index()
    df_with_p_values["p_value_bh_fdr"] = bh_fdr(df_with_p_values["p_value"])
    df_with_p_values["significant_raw"] = df_with_p_values["p_value"] < 0.05
    df_with_p_values["significant_bh_fdr"] = df_with_p_values["p_value_bh_fdr"] < 0.05
    return df_with_p_values.sort_values("p_value").reset_index(drop=True)


def persist_cell_count_summary(cell_counts: Sequence[Mapping], out: Path | None = None):
    out = out or DEFAULT_CELL_COUNT_SUMMARY_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        writer = DictWriter(
            f, fieldnames=["sample", "total_count", "population", "count", "percentage"]
        )
        writer.writeheader()
        writer.writerows(cell_counts)


def all_sample_cell_population_frequencies_df(session: Session) -> pd.DataFrame:
    stmt = all_sample_cell_population_frequencies_stmt()
    return pd.read_sql(stmt, session.bind)


def baseline_miraclib_melanoma_pbmc_samples_by_project_df(
    session: Session,
) -> pd.DataFrame:
    stmt = baseline_miraclib_melanoma_pbmc_samples_by_project_stmt()
    return pd.read_sql(stmt, session.bind)


def baseline_miraclib_melanoma_pbmc_subjects_by_response_df(
    session: Session,
) -> pd.DataFrame:
    stmt = baseline_miraclib_melanoma_pbmc_subjects_by_response_stmt()
    return pd.read_sql(stmt, session.bind)


def baseline_miraclib_melanoma_pbmc_subjects_by_sex_df(
    session: Session,
) -> pd.DataFrame:
    stmt = baseline_miraclib_melanoma_pbmc_subjects_by_sex_stmt()
    return pd.read_sql(stmt, session.bind)


if __name__ == "__main__":
    with SessionLocal() as session:
        logger.info("Summarizing cell counts")
        cell_counts = (
            session.execute(all_sample_cell_population_frequencies_stmt())
            .mappings()
            .all()
        )
        logger.info(
            "Persisting cell count summary to %s", DEFAULT_CELL_COUNT_SUMMARY_PATH.name
        )
        persist_cell_count_summary(cell_counts)
        logger.info("Done summarizing cell counts")
