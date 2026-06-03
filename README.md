```
                   *       *
          `. ___
                    __,' __`.                _..----....____
        __...--.'``;.   ,.   ;``--..__     .'    ,-._    _.-'
  _..-''-------'   `'   `'   `'     O ``-''._   (,;') _,'
,'________________                          \`-._`-','
 `._              ```````````------...___   '-.._'-:
    ```--.._      ,.                     ````--...__\-.
            `.--. `-`                       ____    |  |`
              `. `.                       ,'`````.  ;  ;`
                `._`.        __________   `.      \'__/`      *
                   `-:._____/______/___/____`.     \  `
                               |       `._    `.    \   *
                               `._________`-.   `.   `.___
                                             `------'`


```


# **E.T.** <small>English Teacher</small>

Sistema personalizado de aprendizado de ingles para falantes de **portugues brasileiro**. Baseado no quadro CEFR (A1-C2) com **6 fronts**: writing, listening, speaking, grammar, vocabulary, pronunciation.

> **Projetado para o [opencode CLI](https://opencode.ai)** — um agente de IA que roda no terminal.
> Use com opencode para ativar o **Modo Estudo** com 7 subagentes especialistas.

---

## Comece por aqui

```bash
# 1. Clone o repositorio
git clone https://github.com/anomalyco/english-teacher.git
cd english-teacher

# 2. Instale o opencode (uma vez)
npm install -g opencode-ai
# ou: curl -fsSL https://opencode.ai/install | bash

# 3. Abra o opencode na pasta do projeto
opencode
```

Pronto! O opencode carrega automaticamente o **Modo Estudo**. Digite `oi` para comecar.

> **Alternativa sem opencode:** `python -m src.main --name "Seu Nome" --target B2`

---

## Fluxo de aprendizado

```
Entrada → @estudo identifica aluno → @classifier (nivelamento CEFR)
  → @builder (plano de modulos) → @teacher (aulas guiadas)
  → @tester (testes) → @material (guia de estudo em .md)
  → @tracker (relatorios de progresso)
  └── @coach (pronuncia, a qualquer momento)
```

### Subagentes

| Nome | Funcao | Quando chamar |
|------|--------|---------------|
| `@classifier` | Entrevista CEFR (A1-C2) | Primeiro acesso ou reclassificacao |
| `@builder` | Plano de modulos sequenciais | Apos classificacao |
| `@teacher` | Aulas guiadas com exercicios | "aula", "explica", "aprender" |
| `@tester` | Testes de nivelamento e modulares | "test", "prova", "quiz" |
| `@material` | Gera guia de estudo (reforco/preview) | Automatico apos testes |
| `@tracker` | Relatorios de progresso e erros | "progresso", "relatorio" |
| `@coach` | Treino de pronuncia (th, schwa, etc) | "pronuncia", "treina" |

> O orquestrador chama os subagentes **automaticamente** conforme a necessidade.

---

## Configuracao inicial

Na primeira execucao, o `@tuto` guia voce na escolha do backend:

| Opcao | Qualidade | Custo | Setup |
|-------|-----------|-------|-------|
| **Ollama + modelo local** 🏆 | Muito boa | Gratuito | ~5min (instalar) |
| **API Key Gemini** | Boa | Gratuito | ~10min (cadastro) |
| **API Key Claude** | Excelente | ~US$0,50/dia | ~10min (cadastro + cartao) |
| **Modo offline (stubs)** | Basica | Gratuito | Nenhum |

Digite `/setup` a qualquer momento para reconfigurar.

---

## Material de estudo (reforco / preview)

Apos cada teste de modulo, o sistema gera automaticamente um guia de estudo em
arquivo `.md` — salvo em `study_materials/` na raiz do projeto:

```
study_materials/
├── A1.1-introductions-and-greetings/
│   ├── reforco.md       (nota < 70% — revisao do modulo)
│   └── preview.md       (nota >= 70% — proximo modulo)
├── A1.2-numbers-and-alphabet/
│   └── ...
```

Cada guia contem:
- **Topicos detalhados** com descritores CEFR
- **Dicas PT-BR** (falsos cognatos, gramatica, fonetica)
- **Onde pesquisar** (British Council, BBC, YouTube, YouGlish)
- **Conteudo recomendado** (YouTube, podcasts, sites por nivel)
- **Dicas praticas** por front (writing, speaking, etc.)

---

## Clean output (TUI)

No opencode TUI, use estes comandos para uma experiencia mais limpa:

| Comando | Efeito |
|---------|--------|
| `/thinking` | Oculta blocos de raciocinio do modelo |
| `/details` | Oculta chamadas de ferramentas (bash, read, edit) |

No Modo Estudo, ambos vem desativados por padrao.

---

## Perfis de aluno (persistencia)

Cada aluno tem um perfil JSON em `src/knowledge/students/<uuid>.json`:

```json
{
  "id": "uuid-v4",
  "name": "Gabriel Pequeno",
  "cefr_level": "A2",
  "front_scores": {"writing": 45, "listening": 60, ...},
  "current_module_id": "mod-003",
  "completed_modules": ["mod-001", "mod-002"],
  "notes": [
    {"text": "Confunde present perfect com simple past", "category": "grammar", "resolved": false}
  ]
}
```

### API de perfis

```python
from src.knowledge.student_store import (
    find_student, create_student, get_student,
    add_note, record_success, resolve_note, update_profile
)
```

- `add_note(uuid, text, "grammar")` — salva observacao automatica
- `record_success(uuid, note_id)` — incrementa acertos consecutivos, resolve ao atingir 10
- `resolve_note(uuid, note_id)` — remove nota quando dificuldade superada

---

## Imersao progressiva (PT-BR → EN)

O idioma se adapta automaticamente ao nivel CEFR:

| Nivel | PT-BR | EN | Comportamento |
|-------|-------|----|---------------|
| A1 | 70% | 30% | Instrucoes e gramatica em PT-BR. Vocabulario em EN |
| A2 | 50% | 50% | Explicacoes mistas, pratica guiada em EN |
| B1 | 30% | 70% | Aula predominantemente EN, gramatica complexa em PT-BR |
| B2 | 10% | 90% | So meta-comentarios em PT-BR |
| C1-C2 | 0% | 100% | Imersao total |

---

## Observacao continua

O sistema monitora interacoes e automaticamente:
- Detecta **erros recorrentes** (3+ ocorrencias do mesmo padrao)
- Salva notas no perfil do aluno
- Remove notas quando o aluno demonstra **10+ acertos consecutivos**
- Propoe testes quando detecta estagnacao ou progresso

---

## Dificuldades PT-BR incorporadas

| Categoria | Exemplos |
|-----------|----------|
| **Falsos cognatos** | actually (na verdade) ≠ atualmente, pretend (fingir) ≠ pretender, library (biblioteca) ≠ livraria, parents (pais) ≠ parentes, push (empurrar) ≠ puxar |
| **Gramatica** | Falta de auxiliares em perguntas (do/does/did), omissao do -s (3a pessoa), preposicoes (depend ON, married TO), present perfect (inexistente em PT-BR) |
| **Fonetica** | /θ/ e /ð/ (th), /h/ aspirado, schwa /ə/, vowel length, word stress, can vs can't |

---

## Estrutura do projeto

```
english teacher/
├── src/                               # Pacote Python
│   ├── factory.py                     # Ponto de entrada unico (init)
│   ├── main.py                        # CLI harness alternativo
│   ├── orchestrator.py                # Roteador por palavras-chave
│   ├── protocol.py                    # AgentProtocol (structural typing)
│   ├── registry.py                    # Central de registro de agentes
│   ├── state.py                       # LearnerState (dataclass)
│   ├── setup.py                       # Gerenciamento de configuracao
│   ├── agents/                        # Agentes Python
│   │   ├── base.py                    # BaseAgent (mixin)
│   │   ├── level_classifier.py        # Classificador CEFR
│   │   ├── module_builder.py          # Construtor de curriculo
│   │   ├── teacher.py                 # Professor
│   │   ├── test_builder.py            # Testes
│   │   ├── study_guide.py             # Material de estudo (reforco/preview)
│   │   ├── progress_tracker.py        # Relatorios
│   │   ├── phonetic_coach.py          # Pronuncia
│   │   └── tuto.py                    # Tutor de configuracao
│   ├── knowledge/                     # Dados e persistencia
│   │   ├── cefr.py                    # Descritores CEFR
│   │   ├── ptbr_phonetics.py          # Dificuldades foneticas PT-BR
│   │   ├── student_store.py           # CRUD de perfis
│   │   ├── setup.json                 # Configuracao salva
│   │   └── students/                  # Perfis JSON
│   └── tools/
│       └── search.py                  # WebSearchTool, KnowledgeBaseTool
├── .opencode/agents/                  # Prompts dos agentes (opencode)
├── .claude/agents/                    # Prompts dos agentes (Claude Code)
├── study_materials/                   # Guias de estudo gerados
├── AGENTS.md                          # Instrucoes para opencode
├── CLAUDE.md                          # Instrucoes para Claude Code
├── opencode.json                      # Configuracao opencode
└── README.md
```

---

## Modelos por agente

| Agente | Modelo | Justificativa |
|--------|--------|---------------|
| `estudo`, `teacher`, `builder` | Claude Sonnet 4 | Equilibrio custo/qualidade |
| `classifier` | Claude Opus 4 | Julgamento analitico fino |
| `coach` | Gemini 2.5 Flash | Gratuito, multimodal (audio) |
| `tester`, `tracker` | Claude Haiku 4 | Rapido e barato |
| `material` | Claude Sonnet 4 | Texto de qualidade |

> O `@coach` usa Gemini como padrao. Se falhar, cai para `@teacher` (Sonnet).

---

## Compatibilidade

### Claude Code

```bash
cd english-teacher
claude
# O CLAUDE.md carrega automaticamente como "Modo Estudo"
```

| Recurso | opencode | Claude Code |
|---------|----------|-------------|
| Ativar modo | `Tab` → "Modo Estudo" | So rodar `claude` |
| Subagents | `@nome` para chamar | Fale em portugues |
| Troca de modelo | `opencode.json` | Usa modelo da conta |
| Audio (pronuncia) | `@coach` via Gemini | Nao processa audio |
| Perfis de aluno | `student_store.py` | Funciona igual |

---

## Requisitos

- **Python 3.14+** (stdlib puro, sem dependencias)
- **opencode CLI** (recomendado) ou Claude Code
