from sqlalchemy.orm import Session
from csv import DictReader
from pathlib import Path
from db import engine, SessionLocal
from models import Base, Project, Subject, Sample

CSV_PATH = Path("cell-count.csv")


def initialize_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _fill_projects(session: Session):
    with CSV_PATH.open("r", newline="") as f:
        reader = DictReader(f)
        project_names = set()
        for row in reader:
            project_names.add(row["project"])
    session.add_all(Project(id=name) for name in project_names)
    session.commit()


def _fill_subjects(session: Session):
    with CSV_PATH.open("r", newline="") as f:
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
                    age=row["age"],
                    sex=row["sex"],
                    treatment=row["treatment"],
                    project_id=row["project"],
                    response=response_,
                )
    session.add_all(list(subjects_by_id.values()))
    session.commit()


def _fill_samples(session: Session):
    with CSV_PATH.open("r", newline="") as f:
        reader = DictReader(f)
        session.add_all(
            [
                Sample(
                    id=row["sample"],
                    sample_type=row["sample_type"],
                    time_from_treatment_start=row["time_from_treatment_start"],
                    b_cell=row["b_cell"],
                    cd8_t_cell=row["cd8_t_cell"],
                    cd4_t_cell=row["cd4_t_cell"],
                    nk_cell=row["nk_cell"],
                    monocyte=row["monocyte"],
                    subject_id=row["subject"],
                )
                for row in reader
            ]
        )
    session.commit()


def load_data():
    with SessionLocal() as session:
        _fill_projects(session)
        _fill_subjects(session)
        _fill_samples(session)


if __name__ == "__main__":
    initialize_db()
    load_data()
