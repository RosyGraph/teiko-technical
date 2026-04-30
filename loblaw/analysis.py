import logging
from collections.abc import Mapping, Sequence
from csv import DictWriter
from dataclasses import dataclass
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
    baseline_miraclib_melanoma_pbmc_samples_stmt,
    baseline_miraclib_melanoma_pbmc_subjects_by_response_stmt,
    baseline_miraclib_melanoma_pbmc_subjects_by_sex_stmt,
    miraclib_melanoma_pbmc_response_cell_frequencies_stmt,
)

DEFAULT_CELL_COUNT_SUMMARY_PATH = Path("reports/cell_counts_summary.csv")
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BaselineSubsetTables:
    samples_by_project: pd.DataFrame
    subjects_by_response: pd.DataFrame
    subjects_by_sex: pd.DataFrame


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


def baseline_miraclib_melanoma_pbmc_samples_df(session: Session):
    stmt = baseline_miraclib_melanoma_pbmc_samples_stmt()
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


def load_baseline_subset_tables() -> BaselineSubsetTables:
    with SessionLocal() as session:
        samples_by_project_df = baseline_miraclib_melanoma_pbmc_samples_by_project_df(
            session
        )
        samples_by_project_df = samples_by_project_df.rename(
            columns={"project": "Project", "sample_count": "Samples"}
        )

        subjects_by_response_df = (
            baseline_miraclib_melanoma_pbmc_subjects_by_response_df(session)
        )
        subjects_by_response_df = subjects_by_response_df.rename(
            columns={"response": "Response", "subject_count": "Subjects"}
        )
        subjects_by_response_df["Response"] = subjects_by_response_df["Response"].apply(
            lambda r: "Responder" if r else "Non-responder"
        )

        subjects_by_sex_df = baseline_miraclib_melanoma_pbmc_subjects_by_sex_df(session)
        subjects_by_sex_df = subjects_by_sex_df.rename(
            columns={"sex": "Sex", "subject_count": "Subjects"}
        )
    return BaselineSubsetTables(
        samples_by_project=samples_by_project_df,
        subjects_by_response=subjects_by_response_df,
        subjects_by_sex=subjects_by_sex_df,
    )
