# .memory/ — Sistema de Memória Dinâmica do Projeto

> Aprende padrões de código, workflow e decisões do time de desenvolvimento.
> **ISOLADO** dos agents de estudo (Modo Estudo) — estes NUNCA acessam `.memory/`.

## Para humanos

Leia os arquivos `.md` aqui para entender os padrões do projeto antes de codar.

## Para AI agents

Leia `.memory/AGENTS.md` para instruções de como usar o sistema.

## Arquivos

Os arquivos são criados **dinamicamente** conforme padrões são identificados:

| Arquivo | Criado quando | Contém |
|---|---|---|
| `patterns.md` | Primeiro padrão detectado | Padrões genéricos (bucket inicial) |
| `workflow.md` | 3+ padrões de workflow | Test-first, commit, review |
| `code-style.md` | 3+ padrões de código | Naming, imports, patterns |
| `decisions.md` | 3+ decisões arquiteturais | ADRs |
| `technical.md` | 3+ padrões técnicos | Segurança, desempenho, erro |

A separação é automática via `MemoryManager.optimize()`.

## Isolamento

```
.memory/          ← SÓ agents de desenvolvimento
src/agents/       ← SÓ study agents (NUNCA veem .memory/)
src/knowledge/    ← Conhecimento de ensino (CEFR, fonética)
```

Nenhum study agent (classifier, builder, teacher, tester, tracker, coach, material, tuto)
tem acesso ou conhecimento de `.memory/`.
