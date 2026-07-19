---
id: ADR-0002
title: Switch persistence to DynamoDB
status: accepted
date: 2026-07-19
supersedes: ADR-0001
superseded_by: null
---

# ADR-0002 - Switch persistence to DynamoDB

## Context

Write volume grew and Postgres horizontal scaling became an operational
bottleneck. This is exactly the "it was A, now it is B" case: ADR-0001 said
Postgres; this decision supersedes it.

## Decision

Migrate the payments module's persistence to DynamoDB.

## Consequences

- Horizontal scale and predictable latency.
- Loses native multi-item transactions - idempotency handled in the
  application.
- **Required action:** SPEC-001 was updated (v3) to reflect DynamoDB, and
  ADR-0001 was marked `superseded`.

## Related

- Supersedes: ADR-0001
- Reflected in: SPEC-001 (v3)
