# Convenção de artefatos para SDD com Agents

Um padrão para impedir que specs/plans antigos (que dizem "A") briguem com os
novos (que dizem "não é A, é B") e degradem o raciocínio dos agents.

O gargalo **não** é volume de artefatos — é falta de fonte única de verdade e de
marcação de obsolescência. Vetorizar tudo (Obsidian/RAG) não resolve, porque
embedding mede similaridade, não recência nem autoridade: um retriever traz com
prazer o chunk que diz "A" e o que diz "B" na mesma resposta. A correção é
**governança de ciclo de vida**, não retrieval. RAG entra depois, como
conveniência de busca numa base grande — não como o conserto.

---

## A ideia central: 3 camadas por mutabilidade

Quase todo artefato de SDD é uma destas três coisas, e cada uma tem uma política
de mutação diferente. Misturar as três no mesmo arquivo é o que gera a confusão.

| Camada       | Pergunta que responde   | Mutabilidade                    | Onde vive          |
|--------------|-------------------------|---------------------------------|--------------------|
| **Working**  | Como vamos fazer agora? | Efêmera — descartável ao mergear| `docs/plans/`      |
| **Spec**     | O que deve valer hoje?  | Viva — editada no lugar         | `docs/specs/`      |
| **Decision** | Por que mudou de A→B?   | Imutável — append-only          | `docs/decisions/`  |

Regra de ouro: a **spec** nunca narra história ("antes era X"). Ela descreve só o
presente. A história (o "antes era X, mudamos por Y") mora num **ADR**. E o
**plano** é lixo depois do merge — o que sobrevive graduou-se para spec ou ADR.

---

## Estrutura de pastas

```
repo/
├── CLAUDE.md                     # ponto de entrada do agent: aponta a verdade + regras
└── docs/
    ├── specs/                    # CANÔNICO e vivo — editado no lugar
    │   ├── README.md             #   índice + status de todas as specs ativas
    │   └── 001-example-feature.md
    ├── decisions/                # ADRs — append-only, imutável, o "por quê A→B"
    │   ├── README.md
    │   ├── 0001-example-decision.md
    │   └── 0002-supersede-example.md
    ├── plans/                    # working (Superpowers) — efêmero
    │   ├── active/               #   1 plano por worktree/branch em andamento
    │   └── archive/              #   planos já mergeados (só rastreio)
    ├── _archive/                 # specs aposentadas — invisível ao agent por padrão
    │   └── 2026-01-example-payments-v1.md
    └── scripts/
        └── check-docs.py         # linter de higiene (roda no CI)
```

---

## As regras que fazem funcionar (o segredo não é a pasta, é o header)

Todo doc durável carrega **frontmatter legível por máquina**. É o que permite ao
agent (e ao linter) saber o que é canônico sem ler o conteúdo inteiro.

Spec:

```yaml
---
id: SPEC-001
status: active        # draft | active | superseded | archived
version: 3
updated: 2026-07-19
superseded_by: null
canonical: true       # agents só confiam em canonical:true + status:active
---
```

ADR:

```yaml
---
id: ADR-0002
status: accepted      # proposed | accepted | superseded | deprecated | rejected
supersedes: ADR-0001
superseded_by: null
---
```

Ciclo de vida, em 4 regras:

1. **Specs são vivas.** Edite no lugar, suba `version`/`updated`. Nunca crie
   `pagamentos-v2.md` ao lado de `pagamentos.md`.
2. **Contradição exige ADR.** Toda mudança de comportamento que contraria uma
   decisão anterior cria um novo ADR com `supersedes:` apontando pro antigo, e o
   antigo vira `status: superseded`. O ADR é o **único** lugar onde a
   contradição pode existir legitimamente.
3. **Aposente, não delete.** Spec retirada → `status: archived`, `superseded_by`
   preenchido, arquivo movido para `docs/_archive/`. ADR nunca é deletado.
4. **Plano é descartável.** Ao mergear, promova o durável (→ spec ou ADR) e mova
   o plano para `plans/archive/`. Agent não infere estado atual de um plano.

O `CLAUDE.md` codifica a **ordem de autoridade** para o agent: spec ativa > código
> ADR > archive (ignorado). Assim, quando spec e código divergem, há uma regra
determinística de quem vence — em vez de o agent adivinhar.

---

## Playbook de retrofit (para o que já está bagunçado)

Não tente reescrever tudo. Faça uma passada de triagem:

1. **Inventário sem ler tudo.** Liste caminhos + datas dos artefatos (não jogue o
   conteúdo todo no contexto). Um agent com um `ls -R` e `git log` basta.
2. **Triagem em 3 baldes** por artefato: *canônico* (é a verdade hoje),
   *histórico* (uma decisão passada) ou *morto* (obsoleto sem valor).
3. **Um canônico por domínio.** Escolha/mescle numa única spec viva em
   `docs/specs/`. Onde houver duas versões, a verdade atual vai pra ela.
4. **Toda contradição vira ADR.** Para cada "A→B" que você encontrar, escreva um
   ADR curto capturando a mudança e alinhe a spec canônica ao B.
5. **Histórico/morto → `_archive/`** com `status: archived` + `superseded_by`.
   Não delete (o git guarda, mas o header deixa a intenção explícita).
6. **Escreva o `CLAUDE.md`** apontando para o conjunto canônico e as regras.
7. **Ligue o linter no CI** (`check-docs.py`) pra não regredir.

Dá pra fazer domínio por domínio — não precisa ser big bang. Comece pelo domínio
onde os agents mais se confundem.

---

## Isso já existe? Sim — não é problema novo

Você está reinventando (com razão) coisas que já têm forma madura. O padrão acima
é essencialmente a costura destas peças:

- **ADR / MADR** — o formato de registro de decisão. O campo `status` com
  `superseded` foi feito **exatamente** para o caso "A virou B". É a peça mais
  battle-tested aqui. (https://adr.github.io/madr/)
- **GitHub Spec Kit** — toolkit de SDD que formaliza `constitution.md` (princípios
  do projeto) + `specs/NNN-feature/` com artefatos spec → plan → tasks. Ótima
  referência de scaffolding; o conceito de *constitution* mapeia no teu
  `CLAUDE.md`. (https://github.com/github/spec-kit)
- **AGENTS.md** — padrão cross-tool de arquivo de memória do agent. No Claude Code
  o equivalente é o `CLAUDE.md` (mesma ideia, nome diferente).
- **Superpowers** (Jesse Vincent) — teu fluxo atual. Ele já te dá a camada
  **working**: brainstorm → worktree → plano → implementar, com plano em markdown
  e checkboxes. O que falta é a camada durável com marcação de verdade — é
  justamente o que esta convenção adiciona por cima, sem brigar com ele: o plano
  do Superpowers vive em `docs/plans/`, e no merge você promove pra `specs/`/`decisions/`.
- **"Governing specs" / trace metadata** — a ideia de versionar specs como código
  e registrar qual versão de spec produziu cada comportamento. Útil quando o time
  cresce. (https://www.truefoundry.com/blog/spec-driven-development-ai-agents)

O que **nenhuma** delas é: um vetorizador que resolve contradição. Todas atacam o
problema pelo lado da governança/estado — que é o lado certo.

---

## Onde o Obsidian/RAG realmente entra

Não como fonte de verdade, e sim como **índice de busca por cima do conjunto
canônico**, quando ele fica grande demais pra um agent varrer por `ls`/grep.
Regra: só indexe o que tem `status: active`/`canonical: true`. Nunca vetorize o
`_archive/`. Assim o retrieval nunca ressuscita o "A" antigo — porque o "A" antigo
simplesmente não está no índice.

---

## Arquivos deste pacote

- `README.md` — este documento (a convenção).
- `scaffold/` — estrutura pronta pra copiar num repo, com exemplos preenchidos:
  - `CLAUDE.md`, `docs/specs/`, `docs/decisions/` (com um par ADR-0001→ADR-0002
    demonstrando supersede), `docs/plans/`, `docs/_archive/` e
    `scripts/check-docs.py`.
- O linter passa no exemplo limpo e falha quando você introduz duas specs ativas
  com o mesmo id ou um doc arquivado sem `superseded_by`.
