from sqlalchemy import create_engine

from app.core.database import check_database


def test_database_check_returns_false_when_connection_fails(tmp_path) -> None:
    # SQLite cannot create this database because its parent directory does not exist.
    missing_parent_url = f"sqlite:///{tmp_path / 'missing' / 'nested' / 'db.sqlite'}"
    engine = create_engine(missing_parent_url)
    try:
        assert check_database(engine) is False
    finally:
        engine.dispose()
