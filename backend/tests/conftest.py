import os

# Point the app at the TEST database before anything imports it, so the production
# DATABASE_URL can never be touched by the suite. Default: private in-memory SQLite;
# set TEST_DATABASE_URL to run the same tests against Postgres (CI does).
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite://")
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app import models  # noqa: E402,F401
from app.db import Base, get_db, make_engine  # noqa: E402
from app.main import app  # noqa: E402

engine = make_engine(TEST_DATABASE_URL)
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


BACKEND_DIR = Path(__file__).resolve().parents[1]


def alembic_config(connection) -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    cfg.attributes["connection"] = connection  # migrate the test engine, not DATABASE_URL
    return cfg


@pytest.fixture(scope="session", autouse=True)
def migrated_db():
    """Build the schema with the real Alembic migrations before any test runs."""
    with engine.begin() as conn:
        command.upgrade(alembic_config(conn), "head")
    yield
    with engine.begin() as conn:
        command.downgrade(alembic_config(conn), "base")


@pytest.fixture()
def client(migrated_db):
    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    # Empty every table (children first) so each test starts from a clean, migrated schema.
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture()
def category(client):
    return client.post("/api/categories", json={"name": "Shoes"}).json()


@pytest.fixture()
def product(client, category):
    return client.post(
        "/api/products",
        json={"name": "Runner", "sku": "SKU-1", "price": "49.99", "stock": 20,
              "category_id": category["id"]},
    ).json()


@pytest.fixture()
def customer(client):
    return client.post(
        "/api/customers", json={"name": "Ada Lovelace", "email": "ada@example.com"}
    ).json()
