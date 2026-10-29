# Design decisions

## ADR-001: Start as a modular monolith

**Decision:** Use FastAPI and SQLAlchemy in one deployable application for the initial implementation.

**Reason:** The critical invariants span intents, approvals, spending reservations, and payments. Keeping them in one application and one relational database makes transaction boundaries explicit before any need for service decomposition is demonstrated.

**Trade-off:** The application must maintain clear module boundaries as it grows. Splitting services prematurely would introduce distributed transactions and operational overhead.

## ADR-002: Separate liveness from readiness

**Decision:** `/health` reports process liveness; `/ready` checks database connectivity.

**Reason:** Orchestrators should not restart a healthy process solely because a dependency is temporarily unavailable, while traffic readiness should reflect required dependencies.

## ADR-003: Keep authorization independent of AI

**Decision:** Future AI output can propose a purchase but cannot authorize it.

**Reason:** Model output and external product content are untrusted. Purchase limits, approval binding, and payment state must be enforced by deterministic backend logic.
