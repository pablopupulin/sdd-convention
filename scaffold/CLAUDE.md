# Memória do projeto — LEIA ISTO PRIMEIRO

> Este arquivo é o ponto de entrada de qualquer agent (Claude Code / Superpowers).
> Ele diz **onde está a verdade** e **como saber o que é atual**. Não repita
> conteúdo de spec aqui; aponte para ele.

## Fonte única de verdade (source of truth)

As **únicas** specs canônicas ficam em `docs/specs/` com `status: active` no
frontmatter. Se um documento estiver em `docs/_archive/` ou tiver
`status: superseded`/`archived`, **NÃO** o trate como atual — ele é histórico.

Ordem de autoridade quando houver conflito:

1. `docs/specs/*` com `status: active`  → o que o sistema **deve** fazer hoje
2. O código  → o que ele **faz** hoje
3. `docs/decisions/*` (ADRs)  → **por que** mudou de A para B
4. `docs/_archive/*`  → passado, só para arqueologia. Ignore por padrão.

Se spec e código divergirem, a spec ativa vence: alinhe o código e registre a
reconciliação num ADR. Nunca "corrija" a divergência editando silenciosamente a
spec antiga.

## Como descobrir o que é atual (sem ler tudo)

- `docs/specs/README.md`     → índice das specs ativas + status
- `docs/decisions/README.md` → log de decisões (o "de A para B e por quê")
- `docs/plans/`              → trabalho em andamento (Superpowers). Efêmero.

## Regras para agents ao editar documentação

1. **Specs são vivas.** Edite a spec no lugar e suba `version`/`updated`.
   NUNCA crie `pagamentos-v2.md` ao lado de `pagamentos.md`.
2. **Toda mudança de comportamento que contradiz uma decisão anterior exige um
   novo ADR** em `docs/decisions/` com `supersedes: ADR-XXXX`. O ADR é o único
   lugar onde a contradição pode viver.
3. **Nunca delete um ADR.** Marque `status: superseded` e crie o novo.
4. **Aposente specs, não delete.** Ao retirar uma spec: `status: archived`,
   preencha `superseded_by`, e mova o arquivo para `docs/_archive/`.
5. **Planos do Superpowers** vivem em `docs/plans/active/` enquanto abertos e vão
   para `docs/plans/archive/` quando o PR/worktree é mergeado. O que for durável
   graduou-se para uma spec ou um ADR — o plano em si é descartável.

## Fluxo Superpowers ↔ camada durável

Brainstorm → worktree → plano → implementar (Superpowers) produz artefatos
**working** (efêmeros). No fim de cada feature, promova o que sobreviver:

- Comportamento novo/alterado → atualize a **spec** canônica em `docs/specs/`.
- Escolha de arquitetura/trade-off → escreva um **ADR** em `docs/decisions/`.
- O plano vai para `docs/plans/archive/`. Não é fonte de verdade.
