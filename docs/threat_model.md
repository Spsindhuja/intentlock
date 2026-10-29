# Threat model (initial scope)

## Assets

Future protected assets include user purchase intent, approval records, spending budgets, payment state, provider credentials, webhook secrets, and audit history.

## Trust boundaries

- HTTP clients and AI agents are untrusted callers.
- Product/catalog text is untrusted data, not executable policy.
- The database and payment provider are external dependencies with failure modes.
- Environment variables are the configuration boundary for credentials.

## Threats to address in later milestones

| Threat | Required mitigation |
|---|---|
| Malicious or compromised agent | Authenticated agent identity; server-side authorization and per-agent limits |
| Prompt injection in catalog data | Treat content as data; never let it modify policy |
| Approval replay | Persistent, single-use approval consumption bound to a snapshot |
| Price/merchant/product mutation | Canonical snapshot hash and pre-execution revalidation |
| Concurrent budget overspend | Transactional reservations, locking/constraints, concurrency tests |
| Duplicate execution | Persistent idempotency key plus request-payload fingerprint |
| Provider timeout after success | Mark outcome unknown; reconcile with provider before retrying |
| Forged or duplicated webhook | HMAC/signature verification, persistent event deduplication, idempotent transitions |
| Audit history rewrite | Append-only application behavior and hash chaining; external anchoring needed against privileged rewrite |
| Secret leakage | Environment-based configuration, redacted structured logs, no raw card credentials |

## Current limitations

Milestone 1 has no authentication, payment processing, domain authorization, webhook endpoint, or audit records. Do not expose this foundation as a production payment authorization service.
