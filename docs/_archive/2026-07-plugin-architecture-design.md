---
id: SPEC-001
title: Plugin architecture — original brainstorm design (archived)
status: archived
version: 0
updated: 2026-07-19
supersedes: []
superseded_by: SPEC-001@active
canonical: false
---

> ARCHIVED 2026-07-19. This is the original brainstorming design (in Portuguese)
> that produced the plugin. It is history, not current truth. Its durable
> content graduated to SPEC-001 (`docs/specs/001-plugin-architecture.md`) and
> ADR-0001..ADR-0004 (`docs/decisions/`). Do not treat anything below as current
> behavior; consult the active spec instead. Body kept verbatim, as archived.

# Design: Plugin `sdd-convention` para Claude Code (+ outros agents)

**Data:** 2026-07-19
**Status:** aprovado em brainstorming
**Contexto:** transformar a convenção SDD deste repo (README.md + scaffold/) num
plugin instalável que força a etapa final de gerar/atualizar documentação como
fonte única de verdade.

## Objetivo

Um plugin do Claude Code, publicado num repo GitHub público e instalável em um
comando, que:

1. Ensina o agent a convenção de 3 camadas (working / spec / decision) e a ordem
   de autoridade — sempre que ele tocar em documentação durável.
2. **Força** uma etapa final em todo trabalho que mudou código: atualizar
   spec/ADR ou declarar explicitamente por que nada durável mudou.
3. Oferece um modo de **retrofit interativo** para bases existentes bagunçadas e
   um modo de **setup limpo** para projetos novos.
4. Funciona (na camada de instruções) também em outros agents via o padrão
   Agent Skills + snippet de AGENTS.md.

## Decisões tomadas (com o usuário)

| Decisão | Escolha |
|---|---|
| Formato de distribuição | Plugin Claude Code + compatibilidade com outros agents |
| Mecanismo de enforcement | Stop hook (determinístico) + skill (julgamento) |
| Modo retrofit | Interativo, aprovação por domínio |
| Gatilho do enforcement contínuo | Fim do turno (Stop hook) |
| Idioma do plugin | Inglês (docs gerados seguem o idioma do projeto alvo) |
| Repo | `pablopupulin/sdd-convention`, público |
| Arquitetura | B — skills modulares (3 skills pequenas) |

## Estrutura do repo (= marketplace + plugin)

```
sdd-convention/
├── .claude-plugin/
│   ├── plugin.json          # nome, versão, descrição, autor
│   └── marketplace.json     # lista o próprio plugin (source: ".")
├── skills/
│   ├── sdd-source-of-truth/SKILL.md
│   ├── sdd-finalize/SKILL.md
│   └── sdd-retrofit/SKILL.md
├── commands/
│   ├── sdd-init.md
│   └── sdd-retrofit.md
├── hooks/
│   ├── hooks.json           # registra o Stop hook
│   └── check-docs-updated.py
├── scaffold/                # estrutura docs/ + check-docs.py (asset do /sdd-init)
├── templates/               # spec.md e adr.md com frontmatter pronto
├── tests/                   # fixtures de transcript + testes do hook
├── .github/workflows/ci.yml # pytest do hook + check-docs.py no scaffold
└── README.md                # convenção em EN + install (Claude Code e outros)
```

Instalação: `/plugin marketplace add pablopupulin/sdd-convention` →
`/plugin install sdd-convention`.

## As 3 skills

### `sdd-source-of-truth`
- **Gatilho (description):** ler/editar qualquer coisa em `docs/specs/`,
  `docs/decisions/`, `docs/_archive/`, ou responder "qual o comportamento
  atual do sistema".
- **Conteúdo (~150 linhas):** modelo de 3 camadas por mutabilidade; ordem de
  autoridade (spec ativa > código > ADR > archive); schemas de frontmatter de
  spec e ADR; as 4 regras de ciclo de vida (specs vivas, contradição exige ADR,
  aposentar não deletar, plano é descartável). Referencia `templates/`.

### `sdd-finalize`
- **Gatilho:** terminar uma feature/plano/branch; também é a skill que o Stop
  hook manda invocar no bloqueio.
- **Conteúdo:** checklist de promoção do conhecimento durável:
  1. Comportamento novo/alterado → editar a spec canônica no lugar, subir
     `version` e `updated`.
  2. Decisão de arquitetura ou contradição com decisão anterior → novo ADR com
     `supersedes:`; o antigo vira `status: superseded`.
  3. Plano → `docs/plans/archive/`.
  4. Atualizar o índice em `docs/specs/README.md`.
  5. Rodar `scripts/check-docs.py` se existir.
  6. Se nada durável mudou (refactor puro, typo), declarar isso explicitamente
     ao usuário — é a saída legítima do bloqueio do hook.
- Docs gerados seguem o idioma do projeto alvo (detectado ou perguntado no
  `/sdd-init`).

### `sdd-retrofit`
- **Gatilho:** somente via comando `/sdd-retrofit`.
- **Conteúdo:** playbook interativo:
  1. Inventário sem ler tudo (`ls -R` + `git log` para caminhos/datas).
  2. Propor mapa de domínios ao usuário.
  3. Por domínio: triagem em 3 baldes (canônico / histórico / morto), **com
     aprovação do usuário antes de consolidar**.
  4. Consolidar o canônico numa spec viva por domínio em `docs/specs/`.
  5. Cada contradição "A→B" encontrada vira um ADR curto.
  6. Histórico/morto → `docs/_archive/` com `status: archived` +
     `superseded_by`.
  7. Ao final, executar o equivalente ao `/sdd-init` (scaffold faltante,
     CLAUDE.md, linter/CI).

## Comandos

### `/sdd-init`
- Copia o scaffold para o projeto (`docs/specs|decisions|plans|_archive` +
  `scripts/check-docs.py`).
- Pergunta o idioma dos docs do projeto.
- **Mescla** (nunca sobrescreve) um bloco demarcado
  `<!-- sdd-convention:start -->` … `<!-- sdd-convention:end -->` no
  `CLAUDE.md`/`AGENTS.md` existente, com a ordem de autoridade + regras. O
  demarcador permite atualizar o bloco em upgrades do plugin.
- Idempotente: se estrutura já existe, completa só o que falta e relata.

### `/sdd-retrofit`
- Wrapper fino: invoca a skill `sdd-retrofit`.

## Stop hook (`check-docs-updated.py`)

Registrado em `hooks/hooks.json` no evento `Stop`. Lógica em ordem:

1. Projeto sem `docs/specs/` → exit 0 silencioso (opt-in por projeto; o plugin
   global não incomoda projetos fora da convenção).
2. `stop_hook_active: true` no input JSON → exit 0 (anti-loop; garante no
   máximo 1 bloqueio por turno).
3. Parsear o transcript da sessão (caminho no input), considerando apenas o
   **turno atual** (da última mensagem do usuário até agora): houve
   `Edit`/`Write` em arquivo fora de `docs/`? Qualquer arquivo fora de `docs/`
   conta como "código" — regra simples de propósito; falsos positivos são
   baratos porque a saída legítima do bloqueio é declarar que nada durável
   mudou.
4. Se sim: houve edição em `docs/specs/` ou `docs/decisions/` no mesmo turno?
5. Código mudou e docs não → stdout
   `{"decision": "block", "reason": "<instrui a invocar sdd-finalize: atualizar
   spec/ADR OU declarar por que nada durável mudou>"}`.

Dependência: Python 3 no PATH (a mesma do `check-docs.py`). Sem Python, o hook
**falha aberto** (exit 0) — o enforcement degrada para a camada de skill e o CI;
nunca quebra a sessão do usuário.

## Compatibilidade com outros agents

- Skills no formato aberto Agent Skills (`SKILL.md` + frontmatter
  `name`/`description`) — consumíveis por Codex, Cursor etc.
- README com seção "Other agents": instalação manual (copiar `skills/`) +
  snippet pronto de `AGENTS.md` com ordem de autoridade, as 4 regras e a
  instrução de finalização ("before ending any task that changed code, update
  spec/ADR or state why not"). Hooks são exclusivos do Claude Code; nos demais o
  enforcement é instrucional.

## Testes e validação

- **Hook:** fixtures de transcript para 5 cenários — (a) código sem docs →
  bloqueia; (b) código + spec → passa; (c) sem edições → passa; (d)
  `stop_hook_active` → passa; (e) projeto sem `docs/specs/` → passa. Rodam com
  pytest no GitHub Actions.
- **Linter:** CI roda `check-docs.py` contra o `scaffold/` (caso limpo deve
  passar).
- **Plugin:** antes do push, instalação local via
  `/plugin marketplace add <caminho local>` para confirmar que skills, comandos
  e hook carregam.

## Publicação

1. Reorganizar este diretório para a estrutura acima (README PT atual vira base
   do conteúdo EN; scaffold vira asset).
2. `git init` + primeiro commit.
3. `gh repo create pablopupulin/sdd-convention --public` + push.
4. Teste ponta a ponta da instalação numa sessão limpa.
5. Tag `v0.1.0`.

## Fora de escopo (YAGNI)

- Integração RAG/Obsidian (o README já posiciona como opcional e posterior).
- Hook de PreToolUse em `git commit` (decidido: só Stop hook).
- Publicação em marketplaces de terceiros.
- Suporte a formatos de doc além de Markdown com frontmatter YAML.
