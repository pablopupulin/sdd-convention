---
id: ADR-0001
title: Repo is both marketplace and plugin
status: accepted
date: 2026-07-19
supersedes: null
superseded_by: null
---

# ADR-0001 - Repo is both marketplace and plugin

## Context

The convention had to ship as something installable in one step, from a single
public GitHub repo, without maintaining a separate marketplace repository.

## Decision

Make the repository simultaneously the marketplace and the plugin: ship
`.claude-plugin/marketplace.json` that lists this plugin with `source: "."`
alongside `.claude-plugin/plugin.json`. Both are named `sdd-convention`.

## Consequences

- One-step install: `/plugin marketplace add pablopupulin/sdd-convention` then
  `/plugin install sdd-convention`.
- One repo to version and tag (`v0.1.0`); no split marketplace to keep in sync.
- The plugin name and marketplace name are coupled and must stay
  `sdd-convention` for the documented install commands to keep working.
