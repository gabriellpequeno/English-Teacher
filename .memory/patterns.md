---
updated: 2026-06-08
category: code
count: 10
---

# Código

> Aprendidos automaticamente e confirmados pelo time.

## cs-001: Pure stdlib — zero dependencias externas
- **Status**: confirmed
- **Confidence**: high
- **Category**: code
- **Learned**: 2026-06-08
- **Source**: Analise inicial do codigo existente

Todo codigo Python usa apenas a biblioteca padrao. Nenhum pip install.

### Evidence
- Nao ha requirements.txt
- Nao ha pyproject.toml
- from __future__ import annotations em todo lugar

## cs-002: Structural subtyping com Protocol
- **Status**: confirmed
- **Confidence**: high
- **Category**: code
- **Learned**: 2026-06-08
- **Source**: Analise inicial do codigo existente

Usar typing.Protocol + @runtime_checkable para definir contratos. Nao requer heranca.

### Evidence
- AgentProtocol em src/protocol.py
- isinstance(agent, AgentProtocol) no registry

## cs-003: Dataclasses para modelos de dados
- **Status**: confirmed
- **Confidence**: high
- **Category**: code
- **Learned**: 2026-06-08
- **Source**: Analise inicial do codigo existente

@dataclass + field(default_factory=...) para todos os modelos de estado e config.

### Evidence
- LearnerState, Module, TestResult, ErrorPattern, Interaction em src/state.py

## cs-004: Enum(str, Enum) para valores fixos e comparaveis
- **Status**: confirmed
- **Confidence**: high
- **Category**: code
- **Learned**: 2026-06-08
- **Source**: Analise inicial do codigo existente

Valores com conjunto conhecido viram Enum com str heritage para serializacao natural.

### Evidence
- CefrLevel com __lt__/__le__
- Front com 6 valores fixos

## cs-005: Tools injetadas via **kwargs em BaseAgent
- **Status**: confirmed
- **Confidence**: high
- **Category**: code
- **Learned**: 2026-06-08
- **Source**: Analise inicial do codigo existente

Dependencias externas (WebSearchTool, KnowledgeBaseTool) injetadas no construtor via **kwargs.

### Evidence
- BaseAgent.__init__(**kwargs) em src/agents/base.py
- factory._build_agents() passa tools assim

## dec-001: Conhecimento separado da logica dos agentes
- **Status**: confirmed
- **Confidence**: high
- **Category**: decision
- **Learned**: 2026-06-08
- **Source**: Analise inicial do codigo existente

Dados de dominio (CEFR, fonetica PT-BR) ficam em src/knowledge/, agentes em src/agents/. Agentes consultam via KnowledgeBaseTool.

### Evidence
- src/knowledge/cefr.py e ptbr_phonetics.py sao dados puros
- KnowledgeBaseTool faz a ponte

## dec-002: Roteamento Python por keywords, roteamento AI por @mentions
- **Status**: confirmed
- **Confidence**: high
- **Category**: decision
- **Learned**: 2026-06-08
- **Source**: Analise inicial do codigo existente

Python layer usa intent_map com palavras-chave. AI layer (opencode/Claude) usa @nome nos prompts .md. Nao misturar.

### Evidence
- Orchestrator._pick() com intent_map
- estudo.md chama subagents com @classifier, @teacher etc

## wf-001: Factory.init() como entry point unico
- **Status**: confirmed
- **Confidence**: high
- **Category**: workflow
- **Learned**: 2026-06-08
- **Source**: Analise inicial do codigo existente

Todo harness (CLI, API, teste) chama factory.init() para inicializar o sistema. Nao ha init espalhado.

### Evidence
- src/main.py chama factory.init()
- README.md documenta factory.init() como unico entry point

## wf-002: Dual layer: Python agents + .md definitions
- **Status**: confirmed
- **Confidence**: high
- **Category**: workflow
- **Learned**: 2026-06-08
- **Source**: Analise inicial do codigo existente

Cada agente tem implementacao Python (src/agents/) e definicao em markdown (.opencode/agents/ e .claude/agents/).

### Evidence
- 8 agentes Python + 8 definicoes .opencode + 8 definicoes .claude

## wf-003: Interacoes logadas em LearnerState
- **Status**: confirmed
- **Confidence**: high
- **Category**: workflow
- **Learned**: 2026-06-08
- **Source**: Analise inicial do codigo existente

Toda interacao agente/learner e registrada em state.interactions com timestamp.

### Evidence
- state.add_interaction() chamado no orchestrator e em cada agent.process()
