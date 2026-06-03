# English Teacher (PT-BR → EN)

Sistema personalizado de aprendizado de ingles para falantes de portugues brasileiro. Baseado no quadro CEFR (A1-C2) com 6 fronts de aprendizado: writing, listening, speaking, grammar, vocabulary, pronunciation.

## Requisitos

- **Python 3.14+** (stdlib puro, sem gerenciador de pacotes)
- **Opcional**: [opencode](https://opencode.ai) para usar o **Modo Estudo** com alternancia por Tab
- **Opcional**: [Claude Code](https://docs.anthropic.com/en/docs/claude-code) para uso com CLAUDE.md

## Estrutura do projeto

```
english teacher/
├── src/                               # Pacote Python principal
│   ├── __init__.py
│   ├── factory.py                     # Ponto de entrada unico (init)
│   ├── main.py                        # CLI harness (python -m src.main)
│   ├── orchestrator.py                # Roteador por palavras-chave
│   ├── protocol.py                    # AgentProtocol (Protocol structural)
│   ├── registry.py                    # Central de agentes
│   ├── state.py                       # LearnerState (dataclass)
│   ├── agents/                        # Agentes Python (backend)
│   │   ├── base.py                    # BaseAgent
│   │   ├── level_classifier.py        # Classificador CEFR
│   │   ├── module_builder.py          # Construtor de curriculo
│   │   ├── teacher.py                 # Professor
│   │   ├── test_builder.py            # Testes
│   │   ├── progress_tracker.py        # Relatorios
│   │   └── phonetic_coach.py          # Pronuncia
│   ├── knowledge/                     # Dados e persistencia
│   │   ├── cefr.py                    # Descritores CEFR (Council of Europe)
│   │   ├── ptbr_phonetics.py          # Dificuldades foneticas PT-BR
│   │   ├── student_store.py           # Gerenciamento de perfis
│   │   └── students/                  # Perfis dos alunos (JSON)
│   └── tools/
│       └── search.py                  # WebSearchTool, KnowledgeBaseTool
├── .opencode/agents/                  # Prompts dos agents (formato opencode)
│   ├── estudo.md                      # Orquestrador primario
│   ├── classifier.md, builder.md, teacher.md, tester.md, tracker.md, coach.md
├── .claude/agents/                    # Prompts dos agents (formato Claude Code)
├── AGENTS.md                          # Instrucoes para opencode
├── CLAUDE.md                          # Instrucoes para Claude Code
├── opencode.json                      # Configuracao opencode (default_agent, modelos)
└── README.md
```

## Uso basico (CLI)

```bash
# Listar agentes disponiveis
python -m src.main --list

# Iniciar sessao com nome e nivel alvo
python -m src.main --name "Gabriel Pequeno" --level A2 --target B2
```

## Modo Estudo (opencode)

1. Abra o opencode na pasta do projeto
2. Pressione `Tab` para selecionar o **Modo Estudo**
3. Digite "oi" — o orquestrador vai:
   - Perguntar seu nome completo
   - Buscar perfil existente em `src/knowledge/students/`
   - Se novo: criar perfil e chamar `@classifier` para nivelamento
   - Se retorno: mostrar resumo do progresso e perguntar o que fazer

### Fluxo de aprendizado

```
Entrada → @estudo identifica aluno → @classifier (nivelamento)
  → @builder (plano de modulos) → @teacher (aulas)
  → @tester (testes) → @tracker (relatorios)
  └── @coach (pronuncia, a qualquer momento)
```

### Subagents

| Nome | Funcao | Quando chamar |
|---|---|---|
| `@classifier` | Entrevista CEFR (A1-C2) | Primeiro acesso ou reclassificacao |
| `@builder` | Plano de modulos sequenciais | Apos classificacao |
| `@teacher` | Aulas guiadas com exercicios | "aula", "explica", "aprender" |
| `@tester` | Testes de nivelamento e modulares | "test", "prova", "quiz" |
| `@tracker` | Relatorios de progresso e erros | "progresso", "relatorio" |
| `@coach` | Treino de pronuncia (th, schwa, etc) | "pronuncia", "treina" |

O orquestrador **chama os subagents automaticamente** conforme a necessidade — voce nao precisa alternar entre eles.

## Perfis de aluno (persistencia continua)

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
    {"text": "Dificuldade especial com simple present", "category": "grammar", "resolved": false}
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

## Imersao progressiva (PT-BR → EN)

O idioma das aulas se adapta automaticamente ao nivel CEFR do aluno:

| Nivel | PT-BR | EN | Comportamento |
|---|---|---|---|
| A1 | 70% | 30% | Instrucoes e gramatica em PT-BR. Vocabulario em EN |
| A2 | 50% | 50% | Explicacoes mistas, pratica guiada em EN |
| B1 | 30% | 70% | Aula predominantemente EN, gramatica complexa em PT-BR |
| B2 | 10% | 90% | So meta-comentarios em PT-BR |
| C1-C2 | 0% | 100% | Imersao total |

## Modelos por agente

Cada agente usa o modelo mais adequado para sua funcao, definido em `opencode.json`:

| Agente | Modelo | Justificativa |
|---|---|---|
| `estudo`, `teacher`, `builder` | Claude Sonnet 4 | Equilibrio custo/qualidade |
| `classifier` | Claude Opus 4 | Julgamento analitico fino |
| `coach` | Gemini 2.5 Flash | Gratuito, multimodal (audio) |
| `tester`, `tracker` | Claude Haiku 4 | Rapido e barato |

O `@coach` usa Gemini (gratuito) como padrao. Se falhar ao processar audio, cai para `@teacher` (Sonnet) como fallback.

## Observacao continua

O orquestrador monitora interacoes e automaticamente:
- Detecta erros recorrentes (3+ ocorrencias do mesmo padrao)
- Salva notas no perfil do aluno
- Remove notas quando o aluno demonstra 10+ acertos consecutivos

## Dificuldades PT-BR incorporadas

**Falsos cognatos**: actually, pretend, library, parents, push
**Gramatica**: falta de auxiliares em perguntas, omissao do -s (3a pessoa), preposicoes (depend on, married to), present perfect (inexistente em PT-BR)
**Fonetica**: /th/ surdo e sonoro, /h/ aspirado, schwa, vowel length, word stress

## Compatibility

### Claude Code

**Como entrar no Modo Estudo:**

```bash
cd english-teacher
claude
# Pronto — o CLAUDE.md carrega automaticamente.
# Claude ja sabe que eh o professor de ingles.
```

**Diferencas do opencode:**

| Recurso | opencode | Claude Code |
|---|---|---|
| Ativar modo | `Tab` → seleciona "Modo Estudo" | So rodar `claude` na pasta |
| Subagents | `@teacher`, `@classifier`, etc. | Peça diretamente em portugues |
| Troca de modelo | `opencode.json` por agente | Usa modelo da sua conta |
| Audio (pronuncia) | `@coach` via Gemini | Nao processa audio nativamente |
| Perfis de aluno | Funciona (`src.knowledge.student_store`) | Funciona igual |

**Dicas de uso no Claude Code:**
- Nao precisa de comandos especiais — fale naturalmente: "me classifica", "quero aula de present perfect", "testa meu progresso"
- Os arquivos em `.claude/agents/` servem como referencia de contexto, mas voce nao precisa chama-los com `@`
- O CLAUDE.md ja instrui Claude a agir como "Modo Estudo" desde a primeira mensagem

### opencode

Definicoes em `.opencode/agents/` com suporte a `@name` para chamadas de subagents. O `opencode.json` configura modelo, permissoes e agent padrao.
