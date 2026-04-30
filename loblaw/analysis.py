from scipy.stats.mstats import mannwhitneyu
import pandas as pd
import numpy as np
from collections.abc import Sequence, Mapping
import logging
from pathlib import Path
from csv import DictWriter
from sqlalchemy import select, func, Select, RowMapping
from loblaw.models import CellCount, Sample, Subject, Project
from loblaw.db import SessionLocal
from sqlalchemy.orm import Session

DEFAULT_CELL_COUNT_SUMMARY_PATH = Path("reports/cell_counts_summary.csv")
logger = logging.getLogger(__name__)


def select_cell_population_frequencies() -> Select:
    total_count_ann = (
        func.sum(CellCount.count)
        .over(partition_by=CellCount.sample_id)
        .label("total_count")
    )
    stmt = select(
        CellCount.sample_id.label("sample"),
        total_count_ann,
        CellCount.population,
        CellCount.count,
        (100.0 * CellCount.count / total_count_ann).label("percentage"),
    ).order_by(CellCount.sample_id, CellCount.population)
    return stmt


def query_cell_counts(session: Session) -> Sequence[RowMapping]:
    stmt = select_cell_population_frequencies()
    return session.execute(stmt).mappings().all()


def query_miraclib_pbmc_cell_frequencies(session: Session) -> Sequence[RowMapping]:
    freqs = select_cell_population_frequencies().subquery()
    stmt = (
        select(
            freqs.c.sample,
            freqs.c.total_count,
            freqs.c.population,
            freqs.c.count,
            freqs.c.percentage,
            Subject.response,
            Sample.subject_id,
            Sample.time_from_treatment_start,
        )
        .join(Sample, Sample.id == freqs.c.sample)
        .join(Subject, Subject.id == Sample.subject_id)
        .where(
            Sample.sample_type == "PBMC",
            Subject.condition == "melanoma",
            Subject.treatment == "miraclib",
            Subject.response.is_not(None),
        )
    )
    return session.execute(stmt).mappings().all()


def load_miraclib_pbmc_cell_frequencies_df():
    with SessionLocal() as session:
        frequencies = query_miraclib_pbmc_cell_frequencies(session)
    return pd.DataFrame(frequencies)


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


def load_cell_count_summary_df():
    with SessionLocal() as session:
        cell_counts = query_cell_counts(session)
    return pd.DataFrame(cell_counts)


def select_miraclib_melanoma_pbmc_samples_subset():
    return (
        select(
            Sample.id.label("sample"),
            Subject.id.label("subject"),
            Project.id.label("project"),
            Subject.response.label("response"),
            Subject.sex.label("sex"),
            Sample.time_from_treatment_start,
            Sample.sample_type,
            Subject.condition,
            Subject.treatment,
        )
        .join(Subject, Sample.subject_id == Subject.id)
        .join(Project, Subject.project_id == Project.id)
        .where(
            Subject.condition == "melanoma",
            Sample.sample_type == "PBMC",
            Sample.time_from_treatment_start == 0,
            Subject.treatment == "miraclib",
        )
        .order_by(Project.id, Subject.id, Sample.id)
    )


def load_subset_samples_by_project_df():
    subset = select_miraclib_melanoma_pbmc_samples_subset().subquery()
    stmt = (
        select(subset.c.project, func.count(subset.c.sample).label("sample_count"))
        .group_by(subset.c.project)
        .order_by(subset.c.project)
    )
    with SessionLocal() as session:
        return pd.read_sql(stmt, session.bind)


def load_subset_subjects_by_response_df():
    subset = select_miraclib_melanoma_pbmc_samples_subset().subquery()
    subject_count = func.count(func.distinct(subset.c.subject)).label("subject_count")
    stmt = (
        select(subset.c.response, subject_count)
        .group_by(subset.c.response)
        .order_by(subject_count.desc())
    )
    with SessionLocal() as session:
        return pd.read_sql(stmt, session.bind)


def load_select_subset_subjects_by_sex_df():
    subset = select_miraclib_melanoma_pbmc_samples_subset().subquery()
    subject_count = func.count(func.distinct(subset.c.subject)).label("subject_count")
    stmt = (
        select(subset.c.sex, subject_count)
        .group_by(subset.c.sex)
        .order_by(subject_count.desc())
    )
    with SessionLocal() as session:
        return pd.read_sql(stmt, session.bind)


if __name__ == "__main__":
    with SessionLocal() as session:
        logger.info("Summarizing cell counts")
        cell_counts = query_cell_counts(session)
        logger.info(
            "Persisting cell count summary to %s", DEFAULT_CELL_COUNT_SUMMARY_PATH.name
        )
        persist_cell_count_summary(cell_counts)
        logger.info("Done summarizing cell counts")
