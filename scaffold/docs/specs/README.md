# Specs (fonte de verdade viva)

Cada arquivo aqui descreve **o que o sistema deve fazer hoje** para um domínio.
São documentos **vivos**: editados no lugar, versionados por frontmatter, um por
domínio. Não existem "v2" lado a lado — existe a spec e seu histórico no git +
nos ADRs.

## Índice de specs ativas

| ID       | Domínio            | Status   | Versão | Atualizada |
|----------|--------------------|----------|--------|------------|
| SPEC-001 | Módulo de exemplo  | active   | 3      | 2026-07-19 |

> Mantenha esta tabela como o índice legível por humano e por agent. Uma spec
> `archived` sai daqui e vai para `docs/_archive/`.

## Frontmatter obrigatório

```yaml
---
id: SPEC-001
title: Módulo de pagamentos
status: active        # draft | active | superseded | archived
version: 3            # suba a cada mudança de comportamento
updated: 2026-07-19
owner: time-pagamentos
supersedes: []        # ids de specs que esta consolidou
superseded_by: null   # preenchido quando vira archived
canonical: true       # agents só confiam em canonical: true + status: active
---
```
