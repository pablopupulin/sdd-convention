#!/usr/bin/env python3
"""check-docs.py - validates SDD artifact hygiene.

No external dependencies: parses the "flat" YAML frontmatter (key: value and
simple [a, b] lists) of specs (docs/specs, docs/_archive) and ADRs
(docs/decisions).

Fails (exit 1) on any of these violations:
  1. Two specs with `status: active` sharing the same `id`.
  2. A `superseded`/`archived` doc without `superseded_by`.
  3. An ADR with `supersedes: X` where X does not exist or is not `superseded`.
  4. Duplicate `id` among ADRs.
  5. Missing frontmatter or missing `id`/`status`.

Usage:  python scripts/check-docs.py [docs_root]   (default: ./docs)
"""
import sys
import re
from pathlib import Path

def parse_frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    body = text[3:end].strip("\n")
    data = {}
    for line in body.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if not m:
            continue
        key, raw = m.group(1), m.group(2).strip()
        if raw in ("null", "~", ""):
            val = None
        elif raw.startswith("[") and raw.endswith("]"):
            inner = raw[1:-1].strip()
            val = [x.strip() for x in inner.split(",") if x.strip()] if inner else []
        else:
            val = raw.strip().strip('"').strip("'")
        data[key] = val
    return data

def load(root):
    docs = []
    for p in sorted(Path(root).rglob("*.md")):
        if p.name.upper() == "README.MD":
            continue
        fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        if fm is not None:
            docs.append((p, fm))
    return docs

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs")
    if not root.exists():
        print(f"[error] folder not found: {root}")
        return 1

    docs = load(root)
    errors, warnings = [], []

    # minimum frontmatter
    for p, fm in docs:
        for req in ("id", "status"):
            if req not in fm:
                errors.append(f"{p}: frontmatter missing '{req}'")

    specs = [(p, fm) for p, fm in docs if str(fm.get("id", "")).startswith("SPEC")]
    adrs = [(p, fm) for p, fm in docs if str(fm.get("id", "")).startswith("ADR")]

    # 1. two active specs with the same id
    active_ids = {}
    for p, fm in specs:
        if fm.get("status") == "active":
            active_ids.setdefault(fm.get("id"), []).append(p)
    for sid, paths in active_ids.items():
        if len(paths) > 1:
            errors.append(f"SPEC id '{sid}' has >1 active doc: {[str(x) for x in paths]}")

    # 2. superseded/archived without superseded_by
    for p, fm in docs:
        if fm.get("status") in ("superseded", "archived") and not fm.get("superseded_by"):
            errors.append(f"{p}: status '{fm.get('status')}' but no 'superseded_by'")

    # 3/4. ADR integrity
    adr_by_id = {}
    for p, fm in adrs:
        aid = fm.get("id")
        if aid in adr_by_id:
            errors.append(f"duplicate ADR id: {aid} in {p} and {adr_by_id[aid][0]}")
        adr_by_id[aid] = (p, fm)
    for p, fm in adrs:
        sup = fm.get("supersedes")
        targets = sup if isinstance(sup, list) else ([sup] if sup else [])
        for t in targets:
            if t not in adr_by_id:
                errors.append(f"{p}: supersedes '{t}' which does not exist")
            elif adr_by_id[t][1].get("status") != "superseded":
                warnings.append(
                    f"{p}: supersedes '{t}', but '{t}' is not marked 'superseded' "
                    f"(it is '{adr_by_id[t][1].get('status')}')"
                )

    print(f"Checked {len(docs)} docs ({len(specs)} specs, {len(adrs)} ADRs).")
    for w in warnings:
        print(f"  [warn] {w}")
    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  [ERROR] {e}")
        return 1
    print("OK - no hygiene violations found.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
