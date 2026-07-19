# Project memory - READ THIS FIRST

<!-- sdd-convention:start -->
> This section is managed by the sdd-convention plugin. It tells any agent
> **where the truth lives** and **how to tell what is current**. Do not repeat
> spec content here; point to it.

## Single source of truth

The **only** canonical specs live in `docs/specs/` with `status: active` in
the frontmatter. If a document sits in `docs/_archive/` or carries
`status: superseded`/`archived`, do **NOT** treat it as current - it is
history.

Authority order when sources conflict:

1. `docs/specs/*` with `status: active`  - what the system MUST do today
2. The code  - what it actually does today
3. `docs/decisions/*` (ADRs)  - WHY it changed from A to B
4. `docs/_archive/*`  - the past, archaeology only. Ignore by default.

If an active spec and the code diverge, the spec wins: align the code and
record the reconciliation in an ADR. Never "fix" the divergence by silently
editing the old spec.

## How to find what is current (without reading everything)

- `docs/specs/README.md`     - index of active specs + status
- `docs/decisions/README.md` - decision log (the "from A to B and why")
- `docs/plans/`              - work in progress. Ephemeral.

## Rules for agents editing documentation

1. **Specs are living documents.** Edit the spec in place and bump
   `version`/`updated`. NEVER create `payments-v2.md` next to `payments.md`.
2. **Any behavior change that contradicts a previous decision requires a new
   ADR** in `docs/decisions/` with `supersedes: ADR-XXXX`. The ADR is the
   only place where the contradiction may live.
3. **Never delete an ADR.** Mark it `status: superseded` and write the new
   one.
4. **Retire specs, never delete.** When retiring a spec: `status: archived`,
   fill `superseded_by`, move the file to `docs/_archive/`.
5. **Plans** live in `docs/plans/active/` while open and move to
   `docs/plans/archive/` when merged. Anything durable graduates to a spec or
   an ADR - the plan itself is disposable.

## Finishing work

At the end of any task that changed behavior, promote what survives:

- New or changed behavior - update the canonical **spec** in `docs/specs/`.
- Architecture choice / trade-off - write an **ADR** in `docs/decisions/`.
- The plan goes to `docs/plans/archive/`. It is not a source of truth.
<!-- sdd-convention:end -->
