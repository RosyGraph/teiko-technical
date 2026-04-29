from loblaw.logging_config import configure_logging
from loblaw.loader import initialize_db, load_data

if __name__ == "__main__":
    configure_logging()
    initialize_db()
    load_data()
