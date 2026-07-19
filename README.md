# sdd-convention

**Spec-driven development with a single source of truth - as an installable
Claude Code plugin.**

Old specs that say "A" fight new ones that say "actually, B" and quietly
degrade your agent's reasoning. The bottleneck is not artifact volume - it is
the lack of a single source of truth and of obsolescence marking. Embeddings
will not save you: similarity search happily returns the chunk saying "A" and
the chunk saying "B" in the same answer. The fix is **lifecycle governance**,
not retrieval.

This plugin makes an agent:

1. **Know where the truth lives** - a 3-layer convention (living specs,
   append-only decision records, disposable plans) with machine-readable
   frontmatter.
2. **Close the loop** - a Stop hook notices when a turn changed code without
   updating specs/ADRs and makes the agent either update them or explicitly
   state that nothing durable changed.
3. **Migrate existing messes** - an interactive retrofit playbook (inventory,
   per-domain triage with your approval, consolidation, archive).

## Install (Claude Code)

```
/plugin marketplace add pablopupulin/sdd-convention
/plugin install sdd-convention@sdd-convention
```

Then, in each project that should use the convention:

- New/clean project: run `/sdd-init`
- Existing messy docs: run `/sdd-retrofit`

The Stop hook only acts in projects with a recognized spec tree
(`docs/specs/`, or `openspec/specs/` in OpenSpec projects) - installing the
plugin globally does not affect other projects.

## What you get

| Piece | What it does |
|---|---|
| Skill `sdd-source-of-truth` | The convention: 3 layers, authority order, frontmatter schemas, lifecycle rules. Loads when the agent touches durable docs. |
| Skill `sdd-finalize` | The closing checklist: promote changes into specs/ADRs, archive plans, update indexes. Loads when finishing work - and when the hook fires. |
| Skill `sdd-retrofit` | Interactive migration playbook for existing doc bases. |
| `/sdd-init` | Scaffolds `docs/`, merges a managed rules block into CLAUDE.md, installs the hygiene linter. |
| `/sdd-retrofit` | Runs the retrofit playbook. |
| Stop hook | Fail-open reminder: code changed but no spec/ADR touched - finalize before stopping. |
| `scripts/check-docs.py` | CI linter: duplicate active specs, archived docs without `superseded_by`, broken ADR supersede chains. |

## The convention in 60 seconds

Almost every SDD artifact is one of three things, each with its own mutation
policy. Mixing them in one file is what creates confusion.

| Layer        | Question it answers      | Mutability                      | Lives in          |
|--------------|--------------------------|---------------------------------|-------------------|
| **Working**  | How are we doing it now? | Ephemeral - disposable on merge | `docs/plans/`     |
| **Spec**     | What must hold today?    | Living - edited in place        | `docs/specs/`     |
| **Decision** | Why did A become B?      | Immutable - append-only         | `docs/decisions/` |

Golden rule: a **spec** never narrates history ("it used to be X"). It
describes only the present. The history ("it was X, we changed it because Y")
lives in an **ADR**. And a **plan** is garbage after the merge - whatever
survives graduates into a spec or an ADR.

Authority order when sources conflict:

1. `docs/specs/*` with `status: active` - what the system MUST do today
2. The code - what it actually does today
3. `docs/decisions/*` (ADRs) - WHY it changed from A to B
4. `docs/_archive/*` - history. Ignored by default.

Every durable doc carries machine-readable frontmatter (see
`templates/spec.md` and `templates/adr.md`), which is what lets an agent - and
the linter - know what is canonical without reading everything:

```yaml
---
id: SPEC-001
status: active        # draft | active | superseded | archived
version: 3
updated: 2026-07-19
superseded_by: null
canonical: true       # agents only trust canonical: true + status: active
---
```

Four lifecycle rules make it work:

1. **Specs are living.** Edit in place, bump `version`/`updated`. Never
   create `payments-v2.md` next to `payments.md`.
2. **Contradiction requires an ADR.** New ADR with `supersedes:`, old one
   marked `superseded`. The ADR is the only place a contradiction may exist.
3. **Retire, never delete.** `status: archived` + `superseded_by` + move to
   `docs/_archive/`.
4. **Plans are disposable.** Promote the durable part on merge, archive the
   plan.

## Project layout after /sdd-init

```
your-repo/
|- CLAUDE.md                     # agent entry point: managed rules block
|- docs/
|  |- specs/                     # CANONICAL and living - edited in place
|  |  |- README.md               #   index + status of all active specs
|  |- decisions/                 # ADRs - append-only, the "why A became B"
|  |  |- README.md
|  |- plans/                     # working layer - ephemeral
|  |  |- active/
|  |  |- archive/
|  |- _archive/                  # retired specs - invisible to agents
|- scripts/
   |- check-docs.py              # hygiene linter (run it in CI)
```

## Ecosystem adapters

The three layers are the invariant; where the Spec layer lives is adapter
data. v0.2.0 ships two adapters, detected automatically (union - hybrid
projects get both):

| Adapter | Detected by | Durable (satisfies the hook) | Working (ignored) |
|---|---|---|---|
| `native` | `docs/specs/` | `docs/specs/`, `docs/decisions/` | `docs/plans/` |
| `openspec` | `openspec/specs/` | `openspec/specs/`, `docs/decisions/` | `openspec/changes/` |

The Decision layer (ADRs) is always `docs/decisions/` - it is this plugin's
tool-neutral contribution; [OpenSpec](https://github.com/Fission-AI/OpenSpec)
has no equivalent. In an OpenSpec project, `/sdd-init` runs in hybrid mode:
it creates only `docs/decisions/` + the linter + an OpenSpec-flavored rules
block (never a second canonical spec tree), and spec changes keep flowing
through OpenSpec's propose -> apply -> archive.

An optional `.sdd.json` at the project root overrides detection:

````json
{
  "ecosystems": ["openspec"],
  "extra_durable": ["wiki/adr/"],
  "extra_ignore": ["sandbox/"]
}
````

`ecosystems` forces the adapter set (an empty list disables the hook for the
project); `extra_*` append path prefixes; a malformed file falls back to
detection. Adding a future adapter (Spec Kit, ...) is one entry in the hook's
`ECOSYSTEMS` table.

## Using it with other agents (Codex, Cursor, ...)

The skills follow the open [Agent Skills](https://agentskills.io) format
(`SKILL.md` with `name`/`description` frontmatter):

1. Copy the `skills/` directories into your agent's skills location.
2. Add the rules block to your `AGENTS.md` (same content as
   `scaffold/CLAUDE.md` between the `sdd-convention` markers), plus this
   enforcement line - other agents do not run the Stop hook, so the closing
   step must be instructed:

```markdown
## Finishing work (SDD convention)

Before ending any task that changed code: update the canonical spec in
docs/specs/ (bump version/updated) and/or write an ADR in docs/decisions/
for any decision or contradiction - or state explicitly that nothing durable
changed. Never narrate history inside a spec; history lives in ADRs. Then run
`python scripts/check-docs.py docs` if present.
```

## Where RAG/Obsidian fits

Not as the source of truth - as a **search index over the canonical set**,
once it grows too big to scan. Only index `status: active` +
`canonical: true`. Never vectorize `docs/_archive/`. Retrieval can no longer
resurrect the old "A", because the old "A" is simply not in the index.

## Prior art

This packages battle-tested pieces rather than inventing new ones:

- [ADR / MADR](https://adr.github.io/madr/) - decision records; the
  `superseded` status exists precisely for "A became B".
- [GitHub Spec Kit](https://github.com/github/spec-kit) - SDD scaffolding
  (`constitution.md` maps to the CLAUDE.md rules block).
- [OpenSpec](https://github.com/Fission-AI/OpenSpec) - lightweight SDD change
  flow (propose -> apply -> archive); the `openspec` adapter maps its `specs/`
  tree as the Spec layer and adds the Decision layer it lacks.
- [AGENTS.md](https://agents.md) - cross-tool agent memory file.
- [Superpowers](https://github.com/obra/superpowers) - the working layer
  (brainstorm - plan - implement); this convention adds the durable layer on
  top, without fighting it.

None of them is a vectorizer that resolves contradictions - they all attack
the problem through governance and state, which is the right side.

## Development

```
python -m pytest tests/ -v                        # hook tests
python scaffold/scripts/check-docs.py scaffold/docs  # linter self-check
claude plugin validate .                          # manifest validation
```

## License

MIT
