---
description: Set up the SDD convention in this project (docs structure, CLAUDE.md rules block, hygiene linter)
argument-hint: [docs language, e.g. "en" or "pt-BR"]
---

Set up the SDD documentation convention in the current project. Read the
sdd-source-of-truth skill first if you have not this session. Every step is
idempotent: when a piece already exists, leave it untouched and report it.

The plugin's assets live at ${CLAUDE_PLUGIN_ROOT} (scaffold/ and templates/).
If that variable did not expand, locate the sdd-convention plugin directory
under ~/.claude/plugins/.

1. Docs language: use $ARGUMENTS if given; otherwise detect from existing
   project docs; otherwise ask the user.
2. Copy from ${CLAUDE_PLUGIN_ROOT}/scaffold/ into the project whichever of
   these do not exist yet:
   - docs/specs/README.md            (spec index)
   - docs/decisions/README.md        (decision log)
   - docs/plans/README.md, docs/plans/active/.gitkeep, docs/plans/archive/.gitkeep
   - docs/_archive/README.md
   - scripts/check-docs.py
   Do NOT copy the example spec/ADR/archive files (001-example-feature.md,
   0001/0002-*.md, 2026-01-example-payments-v1.md) into real projects.
3. CLAUDE.md rules block:
   - No CLAUDE.md in the project: copy ${CLAUDE_PLUGIN_ROOT}/scaffold/CLAUDE.md.
   - CLAUDE.md exists without the markers: append the section between
     <!-- sdd-convention:start --> and <!-- sdd-convention:end --> (inclusive)
     from the scaffold file.
   - Markers already present: replace the content between them with the
     scaffold's current version (this is how plugin upgrades propagate).
   - If the project uses AGENTS.md instead of CLAUDE.md, apply the same logic
     to AGENTS.md.
4. If the chosen docs language is not English, translate the copied index
   READMEs and the CLAUDE.md block body into it. Keep frontmatter keys and
   status values in English - the linter depends on them.
5. Run `python scripts/check-docs.py docs` and show the output.
6. Report: what was created, what already existed, and suggest adding
   `python scripts/check-docs.py docs` to CI.
