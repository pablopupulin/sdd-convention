# Plans (camada working — efêmera)

Aqui ficam os artefatos **em andamento** do fluxo Superpowers
(brainstorm → worktree → plano → implementar). Eles são descartáveis por design:
servem enquanto a feature está aberta.

```
plans/
├── active/     # planos de features em andamento (1 por worktree/branch)
└── archive/    # planos de features já mergeadas — mantidos só por rastreio
```

## Regra de ciclo de vida

1. Ao começar uma feature, o plano nasce em `active/` (ex.: `active/2026-07-pagamentos-dynamo.md`).
2. Enquanto trabalha, os checkboxes do plano trackeiam progresso (padrão Superpowers).
3. Ao mergear: **promova o durável** e mova o plano para `archive/`.
   - Comportamento novo → atualize a spec em `docs/specs/`.
   - Trade-off de arquitetura → escreva um ADR em `docs/decisions/`.
4. Um plano em `archive/` **não** é fonte de verdade. Agents não devem inferir o
   estado atual a partir dele.

> Por que separar de specs/decisions: plano é *como vamos fazer agora*; spec é
> *o que deve valer*; ADR é *por que decidimos assim*. Três mutabilidades
> diferentes — não misture no mesmo arquivo.
