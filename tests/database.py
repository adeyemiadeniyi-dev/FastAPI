from fastapi.testclient import TestClient
from app.database import get_db
from app.main import app
from app.models import Base

from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest



engine = create_engine(settings.test_database_url, echo=True)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
