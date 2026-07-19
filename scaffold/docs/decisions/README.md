# Decisions (ADRs — log imutável do "por quê")

Aqui vivem as **contradições legítimas**. Quando o sistema muda de A para B,
o "A" não fica solto numa spec fingindo ser atual: ele vira um ADR marcado como
`superseded`, e um novo ADR (`supersedes: ...`) registra o B.

Formato: [MADR](https://adr.github.io/madr/) enxuto. Regras:

- **Append-only.** Nunca edite a decisão de um ADR aceito; nunca delete.
- Ao mudar de ideia, crie um **novo** ADR e marque o antigo `superseded`,
  ligando os dois por `supersedes` / `superseded_by`.
- Numeração sequencial de 4 dígitos: `0001`, `0002`, ...

## Log de decisões

| ADR      | Título                                  | Status     | Supersedes | Data       |
|----------|-----------------------------------------|------------|------------|------------|
| ADR-0001 | Postgres como storage inicial           | superseded | —          | 2026-01-10 |
| ADR-0002 | Trocar persistência para DynamoDB       | accepted   | ADR-0001   | 2026-07-19 |

## Frontmatter obrigatório

```yaml
---
id: ADR-0002
title: Trocar persistência para DynamoDB
status: accepted      # proposed | accepted | superseded | deprecated | rejected
date: 2026-07-19
supersedes: ADR-0001  # ou null
superseded_by: null   # preenchido quando outro ADR o substitui
---
```
