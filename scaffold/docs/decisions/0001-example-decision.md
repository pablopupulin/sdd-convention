---
id: ADR-0001
title: Postgres as initial storage
status: superseded
date: 2026-01-10
supersedes: null
superseded_by: ADR-0002
---

# ADR-0001 - Postgres as initial storage

> STATUS: **superseded by ADR-0002**. Kept for history. Not current.

## Context

At the start of the project we needed simple relational storage with strong
transactions and team familiarity.

## Decision

Use PostgreSQL as the primary database for the payments module.

## Consequences

- ACID transactions out of the box.
- Coupling to the relational model (high horizontal-scaling cost - which is
  what motivated ADR-0002).
