# Architecture — Milestone 1

TrustRail starts as a modular monolith. A single FastAPI application keeps early transaction boundaries visible and reduces operational complexity. PostgreSQL is the target relational store; SQLite is used only as a zero-service local test default during the foundation milestone.

`/health` is a liveness endpoint and intentionally does not depend on the database. `/ready` runs `SELECT 1` against the configured database and returns `503` if the dependency is unavailable. SQLAlchemy engines are created during application startup and disposed during shutdown.

Future authorization decisions will be deterministic backend operations. An LLM will be an untrusted proposal/explanation component and will not override policy decisions.
