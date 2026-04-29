from loblaw.models import Base, Project, Subject, Sample, CellCount
from loblaw.db import engine, SessionLocal
import logging
from sqlalchemy.orm import Session
from csv import DictReader
from pathlib import Path

DEFAULT_CSV_PATH = Path("cell-count.csv")
CELL_POPULATIONS = [
    "b_cell",
    "cd8_t_cell",
    "cd4_t_cell",
    "nk_cell",
    "monocyte",
]
logger = logging.getLogger(__name__)


def initialize_db():
    logging.debug("Initializing db")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def load_project_rows(session: Session, csv_path: Path | None = None):
    csv_path = csv_path or DEFAULT_CSV_PATH
    with csv_path.open("r", newline="") as f:
        reader = DictReader(f)
        project_names = set()
        for row in reader:
            project_names.add(row["project"])
    session.add_all(Project(id=name) for name in project_names)
    session.commit()


def load_subject_rows(session: Session, csv_path: Path | None = None):
    csv_path = csv_path or DEFAULT_CSV_PATH
    with csv_path.open("r", newline="") as f:
        reader = DictReader(f)
        subjects_by_id = {}
        for row in reader:
            subject_id = row["subject"]
            if subject_id not in subjects_by_id:
                response = row["response"]
                if response == "yes":
                    response_ = True
                elif response == "no":
                    response_ = False
                else:
                    response_ = None
                subjects_by_id[subject_id] = Subject(
                    id=subject_id,
                    condition=row["condition"],
                    age=int(row["age"]),
                    sex=row["sex"],
                    treatment=row["treatment"],
                    project_id=row["project"],
                    response=response_,
                )
    session.add_all(list(subjects_by_id.values()))
    session.commit()


def load_cell_sample_rows(session: Session, csv_path: Path | None = None):
    csv_path = csv_path or DEFAULT_CSV_PATH
    with csv_path.open("r", newline="") as f:
        reader = DictReader(f)
        samples_to_add = []
        cell_counts_to_add = []
        for row in reader:
            sample = Sample(
                id=row["sample"],
                sample_type=row["sample_type"],
                time_from_treatment_start=int(row["time_from_treatment_start"]),
                subject_id=row["subject"],
            )
            samples_to_add.append(sample)
            cell_counts_to_add.extend(
                [
                    CellCount(
                        population=population,
                        count=int(row[population]),
                        sample_id=sample.id,
                    )
                    for population in CELL_POPULATIONS
                ]
            )
        session.add_all(samples_to_add)
        session.add_all(cell_counts_to_add)
    session.commit()


def load_data():
    with SessionLocal() as session:
        logger.info("Loading projects")
        load_project_rows(session)
        logger.info("Loading subjects")
        load_subject_rows(session)
        logger.info("Loading samples")
        load_cell_sample_rows(session)
    logger.info("Finished loading data")
