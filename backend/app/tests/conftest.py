import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.services.mentor_service import load_mentors_from_csv
from app.models import User

# Test Database engine (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create test tables and seed 50 mentors once for the test session."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    load_mentors_from_csv(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """Yield an isolated database session per test function."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_student_client(client, db_session):
    """Client authenticated as a student."""
    resp = client.post("/api/v1/auth/demo", json={"role": "student"})
    assert resp.status_code == 200
    return client


@pytest.fixture
def authenticated_admin_client(client, db_session):
    """Client authenticated as a Mesa Administrator."""
    resp = client.post("/api/v1/auth/demo", json={"role": "admin"})
    assert resp.status_code == 200
    return client
