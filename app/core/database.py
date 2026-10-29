"""SQLAlchemy engine creation and minimal database connectivity check."""

from collections.abc import Generator

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker


def create_database_engine(database_url: str) -> Engine:
    """Create an engine with safe local SQLite defaults and pre-ping for server databases."""
    if database_url.startswith("sqlite"):
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            future=True,
        )
    return create_engine(database_url, pool_pre_ping=True, future=True)


def check_database(engine: Engine) -> bool:
    """Return whether a trivial query succeeds; never leak driver details to callers."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Build the session factory used by request-scoped dependencies in later milestones."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_session(factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    """Yield and reliably close a database session."""
    session = factory()
    try:
        yield session
    finally:
        session.close()
