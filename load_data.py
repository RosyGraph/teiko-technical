from loblaw.db import SessionLocal
from loblaw.loader import initialize_db, load_data
from loblaw.logging_config import configure_logging
from loblaw.reports import persist_all_reports, persist_part2_reports

if __name__ == "__main__":
    configure_logging()
    initialize_db()
    with SessionLocal() as session:
        load_data(session)
