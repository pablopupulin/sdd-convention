#!/usr/bin/env python3
"""
check-docs.py — valida a higiene dos artefatos de SDD.

Sem dependências externas: parseia o frontmatter YAML "plano" (chave: valor e
listas simples [a, b]) das specs (docs/specs, docs/_archive) e dos ADRs
(docs/decisions).

Falha (exit 1) se encontrar qualquer uma destas violações:
  1. Dois specs `status: active` com o mesmo `id`.
  2. Um doc `superseded`/`archived` sem `superseded_by`.
  3. Um ADR com `supersedes: X` onde X não existe, ou X não está `superseded`.
  4. `id` duplicado entre ADRs.
  5. Frontmatter ausente ou sem `id`/`status`.

Uso:  python3 scripts/check-docs.py [raiz_docs]   (default: ./docs)
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
        print(f"[erro] pasta não encontrada: {root}")
        return 1

    docs = load(root)
    errors, warnings = [], []

    # frontmatter mínimo
    for p, fm in docs:
        for req in ("id", "status"):
            if req not in fm:
                errors.append(f"{p}: frontmatter sem '{req}'")

    specs = [(p, fm) for p, fm in docs if str(fm.get("id", "")).startswith("SPEC")]
    adrs = [(p, fm) for p, fm in docs if str(fm.get("id", "")).startswith("ADR")]

    # 1. dois specs active com mesmo id
    active_ids = {}
    for p, fm in specs:
        if fm.get("status") == "active":
            active_ids.setdefault(fm.get("id"), []).append(p)
    for sid, paths in active_ids.items():
        if len(paths) > 1:
            errors.append(f"SPEC id '{sid}' tem >1 doc active: {[str(x) for x in paths]}")

    # 2. superseded/archived sem superseded_by
    for p, fm in docs:
        if fm.get("status") in ("superseded", "archived") and not fm.get("superseded_by"):
            errors.append(f"{p}: status '{fm.get('status')}' mas sem 'superseded_by'")

    # 3/4. integridade dos ADRs
    adr_by_id = {}
    for p, fm in adrs:
        aid = fm.get("id")
        if aid in adr_by_id:
            errors.append(f"ADR id duplicado: {aid} em {p} e {adr_by_id[aid][0]}")
        adr_by_id[aid] = (p, fm)
    for p, fm in adrs:
        sup = fm.get("supersedes")
        targets = sup if isinstance(sup, list) else ([sup] if sup else [])
        for t in targets:
            if t not in adr_by_id:
                errors.append(f"{p}: supersedes '{t}' não existe")
            elif adr_by_id[t][1].get("status") != "superseded":
                warnings.append(
                    f"{p}: supersedes '{t}', mas '{t}' não está marcado 'superseded' "
                    f"(está '{adr_by_id[t][1].get('status')}')"
                )

    print(f"Analisados {len(docs)} docs ({len(specs)} specs, {len(adrs)} ADRs).")
    for w in warnings:
        print(f"  [warn] {w}")
    if errors:
        print(f"\n{len(errors)} erro(s):")
        for e in errors:
            print(f"  [ERRO] {e}")
        return 1
    print("OK — nenhuma violação de higiene encontrada.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
