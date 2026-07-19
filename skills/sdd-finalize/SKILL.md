---
name: sdd-finalize
description: Use when finishing a feature, plan, branch, or any task that changed code in a project using the SDD convention (has docs/specs/ or openspec/specs/) - promotes durable knowledge into specs/ADRs so documentation stays the single source of truth. Also invoke when the SDD Stop hook reports that code changed without a docs update.
---

# SDD Finalize

Every task that changed behavior must end by updating the durable
documentation layer. Run this checklist top to bottom. If you have not read
the sdd-source-of-truth skill this session, read it first.

## Checklist

1. **List what changed.** Which behavior is new or altered? Which
   architectural decisions were made? Use your own edits this session and
   `git diff` if available.
2. **Behavior changed?** Native tree: edit the canonical spec in `docs/specs/`
   **in place** - describe the present only, bump `version`, set `updated` to
   today; if no spec covers this domain yet, create one from
   `${CLAUDE_PLUGIN_ROOT}/templates/spec.md` with the next SPEC id. OpenSpec
   project: spec changes go through the OpenSpec flow (propose -> apply ->
   archive) - do not hand-edit `openspec/specs/`; if the change is already
   applied, verify the spec reflects the final behavior.
3. **Decision made, or a previous decision contradicted?** Create a new ADR
   from `${CLAUDE_PLUGIN_ROOT}/templates/adr.md` with the next ADR id. If it
   contradicts an earlier ADR: set `supersedes:` on the new one, and on the
   old one set `status: superseded` plus `superseded_by`.
4. **Plan finished?** Move it from `docs/plans/active/` to
   `docs/plans/archive/`. Anything durable in it must have been promoted in
   steps 2-3 first.
5. **Update the indexes:** the table in `docs/specs/README.md` and the
   decision log in `docs/decisions/README.md`.
6. **Run the linter** if the project has it:
   `python scripts/check-docs.py docs`. Fix violations before finishing.
7. **Nothing durable changed?** (pure refactor, typo, formatting, tooling,
   dependency bump with no behavior change) - say so explicitly to the user
   in one sentence, e.g. "No spec/ADR update needed: pure refactor, no
   behavior change." That statement is the legitimate exit from the Stop
   hook reminder. Never fabricate a doc update to silence it.

## Rules that trip agents up

- Never narrate history in a spec ("previously X"). Present tense only;
  history lives in ADRs.
- One canonical spec per domain. Consolidate; never fork a v2 file.
- Docs follow the project's language, not English by default. Frontmatter
  keys and status values stay in English.
- Updating a plan checkbox is NOT a docs update. Only `docs/specs/` and
  `docs/decisions/` count as durable.
- In OpenSpec projects, editing `openspec/changes/` (proposal, tasks, design)
  is working-layer activity - never a durable docs update. Durable =
  `openspec/specs/` (via the flow) and `docs/decisions/`.
