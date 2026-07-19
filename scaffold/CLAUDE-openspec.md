# Project memory - READ THIS FIRST

<!-- sdd-convention:start -->
> This section is managed by the sdd-convention plugin (OpenSpec variant). It
> tells any agent **where the truth lives** and **how to tell what is
> current**. Do not repeat spec content here; point to it.

## Single source of truth

The **only** canonical specs live in `openspec/specs/` (OpenSpec format, one
capability per folder). A change under `openspec/changes/` is a proposal
about the future, and anything under `openspec/changes/archive/` is history -
neither is current truth.

Authority order when sources conflict:

1. `openspec/specs/*`  - what the system MUST do today
2. The code  - what it actually does today
3. `docs/decisions/*` (ADRs)  - WHY it changed from A to B
4. `openspec/changes/archive/*`  - completed change history. Ignore by default.

If a spec and the code diverge, the spec wins: align the code and record the
reconciliation in an ADR. Never silently edit a spec to match drifted code.

## How to find what is current (without reading everything)

- `openspec/specs/<capability>/spec.md` - current truth per capability
  (use `openspec list` / `openspec validate` when the CLI is available)
- `docs/decisions/README.md` - decision log (the "from A to B and why")
- `openspec/changes/` - work in progress. Ephemeral.

## Rules for agents editing documentation

1. **Spec changes go through the OpenSpec flow** (propose -> apply ->
   archive). Do not hand-edit `openspec/specs/` outside that flow.
2. **Any decision, or contradiction of a previous decision, requires an ADR**
   in `docs/decisions/` - with `supersedes: ADR-XXXX` when it replaces one.
   The ADR is the only place where the contradiction may live.
3. **Never delete an ADR.** Mark it `status: superseded` and write the new
   one.
4. **Changes are disposable.** After archiving a change, the durable "why"
   graduates to an ADR; the archived change folder is a paper trail, not a
   source of truth.

## Finishing work

At the end of any task that changed behavior:

- Behavior change - update the spec via the OpenSpec change flow.
- Architecture choice / trade-off / contradiction - write an **ADR** in
  `docs/decisions/`.
- Nothing durable changed - say so explicitly in one sentence.
<!-- sdd-convention:end -->
