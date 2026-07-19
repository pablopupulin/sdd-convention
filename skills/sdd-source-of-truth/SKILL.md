---
name: sdd-source-of-truth
description: Use when reading or editing anything under docs/specs/, docs/decisions/, docs/_archive/, or openspec/specs/, or when determining what the system's current behavior should be, in a project using the SDD convention (has docs/specs/ or openspec/specs/). Defines the 3-layer model, authority order, ecosystem mapping, frontmatter schemas, and the four lifecycle rules.
---

# SDD Source of Truth

Projects using this convention separate durable documentation into three
layers by mutability. Mixing layers in one file is what causes stale-doc
confusion, so never do it.

| Layer        | Question it answers      | Mutability                      | Location          |
|--------------|--------------------------|---------------------------------|-------------------|
| **Working**  | How are we doing it now? | Ephemeral - disposable on merge | `docs/plans/`     |
| **Spec**     | What must hold today?    | Living - edited in place        | `docs/specs/`     |
| **Decision** | Why did A become B?      | Immutable - append-only         | `docs/decisions/` |

## Ecosystems

The three layers are the invariant; where the Spec layer lives is ecosystem
data. The Decision layer is ALWAYS `docs/decisions/`, in every ecosystem.

| Ecosystem | Spec layer | Working layer | Decision layer |
|---|---|---|---|
| native | `docs/specs/` | `docs/plans/` | `docs/decisions/` |
| OpenSpec | `openspec/specs/` | `openspec/changes/` | `docs/decisions/` |

- The authority order below is identical in every ecosystem - substitute the
  Spec-layer path (in OpenSpec: item 1 is `openspec/specs/*`, item 4 is
  `openspec/changes/archive/*`).
- OpenSpec specs use OpenSpec's own format (Requirements/Scenarios, validated
  by `openspec validate`) - the frontmatter schemas and lifecycle rules below
  govern the native tree. In OpenSpec, behavior retirement is `REMOVED
  Requirements` via a change, not `docs/_archive/`.
- An optional `.sdd.json` at the project root overrides detection:
  `{"ecosystems": ["openspec"], "extra_durable": [...], "extra_ignore": [...]}`.

## Authority order

When sources conflict, trust in this order:

1. `docs/specs/*` with `status: active` - what the system MUST do today
2. The code - what it actually does today
3. `docs/decisions/*` (ADRs) - WHY it changed from A to B
4. `docs/_archive/*` - history only. Ignore by default.

If an active spec and the code diverge, the spec wins: align the code and
record the reconciliation in an ADR. Never silently edit a spec to match
drifted code.

## Frontmatter schemas

Spec (`docs/specs/NNN-domain.md`):

    ---
    id: SPEC-001
    title: Payments module
    status: active        # draft | active | superseded | archived
    version: 3            # bump on every behavior change
    updated: 2026-07-19
    owner: payments-team
    supersedes: []
    superseded_by: null
    canonical: true       # agents only trust canonical: true + status: active
    ---

ADR (`docs/decisions/NNNN-title.md`):

    ---
    id: ADR-0002
    title: Switch persistence to DynamoDB
    status: accepted      # proposed | accepted | superseded | deprecated | rejected
    date: 2026-07-19
    supersedes: ADR-0001  # or null
    superseded_by: null
    ---

Full body templates: `${CLAUDE_PLUGIN_ROOT}/templates/spec.md` and
`${CLAUDE_PLUGIN_ROOT}/templates/adr.md`.

## The four lifecycle rules

1. **Specs are living documents.** Edit in place, bump `version` and
   `updated`. NEVER create `payments-v2.md` next to `payments.md`.
2. **Contradiction requires an ADR.** A behavior change that contradicts a
   previous decision gets a new ADR with `supersedes:` pointing at the old
   one; the old one gets `status: superseded` and `superseded_by` filled. The
   ADR is the ONLY place a contradiction may legitimately exist.
3. **Retire, never delete.** Retired spec: `status: archived`,
   `superseded_by` filled, file moved to `docs/_archive/`. ADRs are never
   deleted.
4. **Plans are disposable.** On merge, promote what survives (to a spec or an
   ADR) and move the plan to `docs/plans/archive/`. Never infer current state
   from a plan.

## Hygiene

- Keep the index table in `docs/specs/README.md` in sync (id, domain, status,
  version, updated) and the decision log in `docs/decisions/README.md`.
- A spec never narrates history ("previously X"). Present tense only; the
  "before" lives in ADRs.
- If `scripts/check-docs.py` exists in the project, run
  `python scripts/check-docs.py docs` after any docs change and fix
  violations.
- Write project docs in the project's language (match existing docs; ask if
  unclear). Frontmatter keys and status values stay in English - the linter
  depends on them.
