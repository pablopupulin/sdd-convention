# Design: Ecosystem adapters (OpenSpec support) — v0.2.0

**Date:** 2026-07-19
**Status:** design approved in brainstorming; implementation plan pending
**Layer:** working (this document is disposable; durable outcome graduates to
SPEC-001 and a new ADR at finalize)

## Goal

Let projects that do SDD with **OpenSpec** (and, later, Spec Kit and others)
use the sdd-convention plugin. The plugin's value is ecosystem-neutral:
lifecycle governance, the append-only Decision layer (ADRs), and deterministic
enforcement (Stop hook + linter). Only the *location and format of the Spec
layer* varies per ecosystem — so that variance becomes data, not architecture.

## Decisions taken (with the user)

| Decision | Choice |
|---|---|
| Scope | Full interop via **descriptive adapters**; v0.2.0 ships `native` + `openspec`; Spec Kit later = new entry |
| ADR home | **Always `docs/decisions/`**, in every ecosystem (tool-neutral Decision layer) |
| Discovery | Auto-detection by union + optional `.sdd.json` override at project root |
| Adapter architecture | Data, not code: one dict entry per ecosystem in the hook; same shape in `.sdd.json` |
| Version | 0.2.0 (plugin.json + marketplace.json + tag) |

## OpenSpec ground truth (verified 2026-07-19)

- `openspec/project.md` — project context
- `openspec/specs/<capability>/spec.md` — current truth (Requirements/Scenario
  format, validated by `openspec validate`)
- `openspec/changes/<change-id>/{proposal.md, specs/, design.md, tasks.md}` —
  in-flight change (working layer)
- `openspec/changes/archive/YYYY-MM-DD-<change-id>/` — completed changes
- Flow: `/opsx:propose` → `/opsx:apply` → `/opsx:archive`

Mapping to our 3-layer model: `openspec/specs/` = Spec layer;
`openspec/changes/` = Working layer; Decision layer = ours (`docs/decisions/`),
OpenSpec has no equivalent.

## The ecosystem model

Each adapter is a descriptive entry with three fields:

- `detect` — directory whose existence arms the hook and selects the adapter
- `durable` — path prefixes that satisfy the docs-updated requirement
- `ignore` — the tool's whole docs tree: edits there neither satisfy nor
  trigger (the generalization of today's blanket `docs/` rule)

| Adapter | `detect` | `durable` | `ignore` |
|---|---|---|---|
| `native` | `docs/specs` | `docs/specs/`, `docs/decisions/` | `docs/` |
| `openspec` | `openspec/specs` | `openspec/specs/`, `docs/decisions/` | `openspec/`, `docs/` |

Rules:

- **Union detection.** A hybrid project (both trees) gets the union of
  `durable` and `ignore`. The hook arms when ANY adapter detects.
- **`openspec/changes/` is working**: editing a proposal/tasks/design does NOT
  count as a durable docs update (same as `docs/plans/` today).
- **`.sdd.json`** (project root, optional) overrides/extends:
  `{"ecosystems": ["openspec"], "extra_durable": ["wiki/adr/"], "extra_ignore": [...]}`.
  `ecosystems` restricts/forces the adapter set (bypasses detection);
  `extra_*` appends prefixes. Missing or malformed file → pure auto-detection
  (fail-open, like everything in the hook).

## Hook changes (`hooks/check-docs-updated.py`)

- Add the `ECOSYSTEMS` dict, `.sdd.json` loading, and prefix-based
  classification (durable / ignore / code). Turn-boundary logic, total
  fail-open, and the polyglot launcher are untouched.
- Arming rule becomes "any adapter detected" (today: `docs/specs` only).
- **Native-mode behavior is byte-identical to v0.1.x** — the existing 18 tests
  must keep passing unmodified.
- ~8 new tests: OpenSpec project blocks on code without durable docs;
  `openspec/specs/` edit satisfies; `openspec/changes/` edit neither satisfies
  nor triggers; `docs/decisions/` satisfies in OpenSpec mode; hybrid project;
  `.sdd.json` forcing an ecosystem; malformed `.sdd.json` fails open; project
  with no adapter stays silent.

## Skill changes

- **`sdd-source-of-truth`**: new "Ecosystems" section — the adapter table plus
  two rules: (1) the authority order is identical in every ecosystem, only the
  Spec-layer path changes; (2) OpenSpec specs use OpenSpec's format
  (Requirements/Scenarios, `openspec validate`) — our frontmatter/lifecycle
  rules govern the native tree; in OpenSpec, behavior retirement is `REMOVED
  Requirements` via a change, not `_archive`.
- **`sdd-finalize`**: checklist gains the OpenSpec branch — spec changes go
  through the `opsx` flow (propose → apply → archive); after archive,
  decisions/contradictions become ADRs in `docs/decisions/`. Editing a change
  is never a durable docs update.
- **`sdd-retrofit`**: new Phase 0 "detect ecosystem". In OpenSpec projects:
  inventory includes `openspec/changes/archive/` as ADR candidates (distill
  each relevant archived change into a short ADR), and consolidation respects
  `openspec/specs/` as the canonical spec tree — never create a parallel
  `docs/specs/`.

## `/sdd-init` adapter-aware (hybrid mode)

When `openspec/` is detected: create only `docs/decisions/` (+README),
`scripts/check-docs.py`, and the CLAUDE.md block in an OpenSpec variant
(authority order pointing at `openspec/specs/`). Do NOT create `docs/specs/`,
`docs/plans/`, or `docs/_archive/` — two competing canonical spec trees is the
exact failure mode this convention exists to prevent. Do not write `.sdd.json`
(auto-detection covers it); mention the override in the report. The linter
keeps linting only our trees (`docs/`); OpenSpec specs belong to
`openspec validate`.

## Docs and release

- README: new "Ecosystem adapters" section (table, `.sdd.json`, hybrid init);
  OpenSpec added to prior art.
- Version 0.2.0 in plugin.json and marketplace.json; tag `v0.2.0`; CI
  unchanged (new tests run in the existing matrix).
- At finalize: bump SPEC-001 (behavior change: ecosystem adapters), write a
  new ADR ("Spec layer location is adapter data; Decision layer is always
  docs/decisions/"), move this plan to `docs/plans/archive/`.

## Out of scope (YAGNI)

- Spec Kit adapter (the extension point exists; ship when there is a user).
- Linting OpenSpec spec files (that is `openspec validate`'s job).
- Generating OpenSpec artifacts (changes/proposals) from our plugin.
- Per-adapter configuration beyond the three `.sdd.json` keys.
