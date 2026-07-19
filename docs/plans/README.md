# Plans (the working layer - ephemeral)

Work-in-progress artifacts live here (brainstorm - worktree - plan -
implement flows such as Superpowers). They are disposable by design: they
serve while the feature is open.

```
plans/
|- active/     # plans for in-flight features (1 per worktree/branch)
|- archive/    # plans of merged features - kept only for the paper trail
```

## Lifecycle rule

1. When a feature starts, its plan is born in `active/`
   (e.g. `active/2026-07-payments-dynamo.md`).
2. While working, the plan's checkboxes track progress.
3. On merge: **promote what is durable**, then move the plan to `archive/`.
   - New behavior - update the spec in `docs/specs/`.
   - Architecture trade-off - write an ADR in `docs/decisions/`.
4. A plan in `archive/` is **not** a source of truth. Agents must not infer
   current state from it.

> Why separate from specs/decisions: a plan is *how we are doing it now*; a
> spec is *what must hold*; an ADR is *why we decided so*. Three different
> mutabilities - never mix them in one file.
