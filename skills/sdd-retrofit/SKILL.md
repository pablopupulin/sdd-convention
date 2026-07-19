---
name: sdd-retrofit
description: Use only when the user runs /sdd-retrofit - interactive playbook to migrate an existing, messy documentation base into the SDD convention through inventory, per-domain triage with user approval, consolidation into living specs, ADRs for contradictions, and archiving.
---

# SDD Retrofit

Interactive migration of an existing project's documentation into the SDD
convention. Read the sdd-source-of-truth skill first. Never bulk-rewrite
without approval: triage is judgment, and a wrong call becomes a wrong source
of truth.

## Phase 0 - Detect the ecosystem

If the project has `openspec/specs/`, the canonical Spec layer is OpenSpec's:
consolidate INTO `openspec/specs/` capabilities and never create a parallel
`docs/specs/`. `openspec/changes/archive/` entries are ADR candidates -
distill each archived change that carried a real decision into a short ADR in
`docs/decisions/`. Everything else in this playbook applies unchanged, with
`openspec/specs/` substituted for `docs/specs/`.

## Phase 1 - Inventory (no deep reading)

1. List doc artifacts with paths and dates only: directory listing of doc
   folders plus, when git is available,
   `git log --format="%ad" --date=short -1 -- <path>` per file. Do NOT load
   full contents into context.
2. Read at most the first ~20 lines of each file - just enough to classify
   its domain and kind.
3. Show the user an inventory table: path, apparent domain, last modified,
   kind (spec-like / plan-like / decision-like / other).

## Phase 2 - Domain map (approval gate)

Propose a domain map: which files belong to which domain, and which single
file (or merge of files) should become the canonical spec of each domain.
Ask the user to approve or correct the map before touching anything. Also ask
which domain confuses agents the most - start there. No big bang: one domain
at a time.

## Phase 3 - Per-domain triage (approval gate per domain)

For the current domain, propose sorting every artifact into 3 buckets:

- **Canonical** - describes today's truth (or its newest version). Becomes or
  merges into the living spec.
- **Historical** - a past decision worth keeping. Distilled into an ADR.
- **Dead** - obsolete, no remaining value. Archived as-is.

Show the buckets and wait for the user's approval of this domain. Then
execute:

1. Consolidate the canonical bucket into ONE living spec at
   `docs/specs/NNN-<domain>.md` using
   `${CLAUDE_PLUGIN_ROOT}/templates/spec.md`. Present tense only - strip any
   "previously X" narration you find while merging.
2. Every "A became B" contradiction found becomes a short ADR from
   `${CLAUDE_PLUGIN_ROOT}/templates/adr.md`, capturing what changed and why.
   Chain `supersedes`/`superseded_by` when one decision replaced another.
3. Move historical and dead originals to `docs/_archive/` with
   `status: archived` and `superseded_by` pointing at the new spec or ADR.
   Prefix archived filenames with the retirement date (YYYY-MM-). Never
   delete.
4. Update the index in `docs/specs/README.md` and the log in
   `docs/decisions/README.md`.

Repeat Phase 3 for the next approved domain.

## Phase 4 - Setup

Finish exactly like /sdd-init, which is ecosystem-aware: native projects get
the full scaffold (index READMEs, `docs/plans/active|archive/`,
`docs/_archive/`, `scripts/check-docs.py`); OpenSpec projects get hybrid mode
(only `docs/decisions/` + linter + the OpenSpec rules block). Merge the
CLAUDE.md rules block, ask about the project docs language, and offer wiring
`check-docs.py` into CI. Then run
`python scripts/check-docs.py docs` and show the result.
