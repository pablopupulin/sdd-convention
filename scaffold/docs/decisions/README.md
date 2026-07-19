# Decisions (ADRs - the immutable "why" log)

This is where **legitimate contradictions** live. When the system changes
from A to B, the "A" does not linger in a spec pretending to be current: it
becomes an ADR marked `superseded`, and a new ADR (`supersedes: ...`) records
the B.

Format: lean [MADR](https://adr.github.io/madr/). Rules:

- **Append-only.** Never edit an accepted ADR's decision; never delete.
- Changed your mind? Write a **new** ADR and mark the old one `superseded`,
  linking both via `supersedes` / `superseded_by`.
- Sequential 4-digit numbering: `0001`, `0002`, ...

## Decision log

| ADR      | Title                             | Status     | Supersedes | Date       |
|----------|-----------------------------------|------------|------------|------------|
| ADR-0001 | Postgres as initial storage       | superseded | -          | 2026-01-10 |
| ADR-0002 | Switch persistence to DynamoDB    | accepted   | ADR-0001   | 2026-07-19 |

## Required frontmatter

```yaml
---
id: ADR-0002
title: Switch persistence to DynamoDB
status: accepted      # proposed | accepted | superseded | deprecated | rejected
date: 2026-07-19
supersedes: ADR-0001  # or null
superseded_by: null   # filled when another ADR replaces this one
---
```
