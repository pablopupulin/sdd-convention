# Specs (the living source of truth)

Each file here describes **what the system must do today** for one domain.
These are **living** documents: edited in place, versioned via frontmatter,
one per domain. There is no "v2 next to v1" - there is the spec, plus its
history in git and in the ADRs.

## Active spec index

| ID       | Domain              | Status | Version | Updated    |
|----------|---------------------|--------|---------|------------|
| SPEC-001 | Plugin architecture | active | 2       | 2026-07-19 |

> Keep this table as the index readable by humans and agents. An `archived`
> spec leaves this table and moves to `docs/_archive/`.

## Required frontmatter

```yaml
---
id: SPEC-001
title: Payments module
status: active        # draft | active | superseded | archived
version: 3            # bump on every behavior change
updated: 2026-07-19
owner: payments-team
supersedes: []        # spec ids this one consolidated
superseded_by: null   # filled when it becomes archived
canonical: true       # agents only trust canonical: true + status: active
---
```
