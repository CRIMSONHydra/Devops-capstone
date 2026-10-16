from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext

from app.db import Base

from .conftest import engine


def test_schema_comes_from_migrations(client):
    with engine.connect() as conn:
        assert "alembic_version" in conn.dialect.get_table_names(conn)


def test_models_match_migrations(client):
    """Fails if a model changed without a matching Alembic migration."""
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    assert diff == []
