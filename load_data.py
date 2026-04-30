from loblaw.loader import initialize_db, load_data
from loblaw.logging_config import configure_logging

if __name__ == "__main__":
    configure_logging()
    initialize_db()
    load_data()
