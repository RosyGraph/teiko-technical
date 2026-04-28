from sqlalchemy.orm import Session
from csv import DictReader
from pathlib import Path
from db import engine, SessionLocal
from models import Base, Project

CSV_PATH = Path("cell-count.csv")


def initialize_db():
    Base.metadata.create_all(bind=engine)


def _fill_projects(session: Session):
    with CSV_PATH.open("r", newline="") as f:
        reader = DictReader(f)
        project_names = set()
        for row in reader:
            project_names.add(row["project"])
    session.add_all(Project(name=name) for name in project_names)
    session.commit()


def load_data():
    with SessionLocal() as session:
        _fill_projects(session)
        # _fill_subjects()
        # _fill_samples()


if __name__ == "__main__":
    initialize_db()
    load_data()
