import pandas as pd
from collections.abc import Mapping
import logging
from pathlib import Path
from csv import DictWriter
from sqlalchemy import select, func
from loblaw.models import CellCount
from loblaw.db import SessionLocal
from sqlalchemy.orm import Session

DEFAULT_CELL_COUNT_SUMMARY_PATH = Path("reports/cell_counts_summary.csv")
logger = logging.getLogger(__name__)


def summarize_cell_counts(session: Session):
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
    return session.execute(stmt).mappings().all()


def persist_cell_count_summary(
    cell_counts: list[Mapping[str, object]], out: Path | None = None
):
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
        cell_counts = summarize_cell_counts(session)
    return pd.DataFrame(cell_counts)


if __name__ == "__main__":
    with SessionLocal() as session:
        logger.info("Summarizing cell counts")
        cell_counts = summarize_cell_counts(session)
        logger.info(
            "Persisting cell count summary to %s", DEFAULT_CELL_COUNT_SUMMARY_PATH.name
        )
        persist_cell_count_summary(cell_counts)
        logger.info("Done summarizing cell counts")
