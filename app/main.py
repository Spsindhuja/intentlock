"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import Engine

from app.api.routes.purchases import router as purchases_router
from app.core.config import settings
from app.core.database import check_database, create_database_engine


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Create infrastructure once per application lifecycle and dispose it on shutdown."""
    engine = create_database_engine(settings.database_url)
    application.state.db_engine = engine
    try:
        yield
    finally:
        engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Intent-bound authorization for AI-assisted purchases.",
    lifespan=lifespan,
)


app.include_router(purchases_router)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Send browser visitors to the interactive API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["operations"], summary="Liveness probe")
def health() -> dict[str, str]:
    """Confirm the process is responding; this does not assert database availability."""
    return {"status": "ok"}


@app.get("/ready", tags=["operations"], summary="Readiness probe")
def ready(request: Request) -> Any:
    """Return ready only when the configured database can execute a trivial query."""
    engine: Engine | None = getattr(request.app.state, "db_engine", None)
    if engine is None or not check_database(engine):
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": "database_unavailable"},
        )
    return {"status": "ready", "dependencies": {"database": "ok"}}
