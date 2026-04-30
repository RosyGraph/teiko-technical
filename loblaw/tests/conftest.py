import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from loblaw.models import Base


@pytest.fixture
def engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine):
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        yield session
