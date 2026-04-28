from db import engine
from sqlalchemy import inspect
from models import Base


def initialize_db():
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    print(inspector.get_table_names())
    for table_name in inspector.get_table_names():
        print(table_name)
        for column in inspector.get_columns(table_name):
            print(" ", column["name"], column["type"], "nullable=", column["nullable"])


def load_data(): ...


if __name__ == "__main__":
    initialize_db()
