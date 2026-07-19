---
id: ADR-0005
title: Ecosystems are descriptive adapter data; the Decision layer is fixed
status: accepted
date: 2026-07-19
supersedes: null
superseded_by: null
---

# ADR-0005 - Ecosystems are descriptive adapter data; the Decision layer is fixed

## Context

Users do SDD with different spec/working ecosystems (the native convention,
OpenSpec today; Spec Kit and others tomorrow). The plugin's value - lifecycle
governance, the ADR layer, deterministic enforcement - is ecosystem-neutral;
only the Spec layer's location and format vary. Options considered: adapters
as Python modules (dynamic loading), everything via a config file, or
descriptive data entries.

## Decision

Each ecosystem is a data entry ({detect, durable, ignore}) in the hook's
ECOSYSTEMS table - no adapter code. Detection unions every ecosystem whose
detect directory exists; an optional .sdd.json ("ecosystems",
"extra_durable", "extra_ignore") forces or extends it, failing open to
detection when malformed. The Decision layer is ALWAYS docs/decisions/, in
every ecosystem. /sdd-init in an OpenSpec project runs hybrid mode and never
creates a second canonical spec tree.

## Consequences

- Adding an ecosystem (Spec Kit, ...) is one dict entry + docs + tests - no
  architecture.
- The hook stays a single stdlib file (ADR-0004 holds) and fail-open
  (ADR-0002 holds).
- OpenSpec projects gain the ADR layer and enforcement without leaving their
  propose -> apply -> archive flow; openspec/changes/ never satisfies the
  hook (working layer).
- Native-mode behavior is unchanged from v0.1.x.
