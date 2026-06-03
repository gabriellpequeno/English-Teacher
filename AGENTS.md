# AGENTS.md

## Project: English Teacher (PT-BR → EN)

PT-BR Portuguese speaker English learning system. CEFR-based (A1-C2) with 6 fronts: writing, listening, speaking, grammar, vocabulary, pronunciation.

## Architecture

- **Entry point**: `init()` from `src.factory` — single call all harnesses (CLI, API, etc.) must use. `python -m src.main` for CLI.
- **CLI harness**: `src/main.py` (argparse: `--name`, `--level`, `--target`, `--list`). Not the main entry — `factory` is.
- **No package manager** for Python — pure stdlib code. Python 3.14+ required (cpython-314 bytecode).
- **Dual layer**: Python agents in `src/agents/` (implement `AgentProtocol`), AI agent definitions in `.opencode/agents/*.md` and `.claude/agents/*.md`.
- **Structural subtyping**: agents don't need to inherit — they just need `name`, `description`, `version`, `tags`, `build_system_prompt()`, `process()`. Use `isinstance(agent, AgentProtocol)` to check.
- **Orchestrator** (`orchestrator.py`) routes by keyword matching — not a registered agent.

## Primary Agent: Modo Estudo

The `estudo` agent (`.opencode/agents/estudo.md`, `mode: primary`) is the main entry point. It orchestrates all 6 specialist subagents:

| Name | Role | Mode |
|------|------|------|
| `estudo` | Orchestrator — greets, identifies, routes | primary |
| `classifier` | CEFR level placement interview | subagent |
| `builder` | Curriculum/module planning | subagent |
| `teacher` | Guided lessons & explanations | subagent |
| `tester` | Placement & module tests | subagent |
| `tracker` | Progress reports & analytics | subagent |
| `coach` | Pronunciation coaching | subagent |

**Key**: If `state.test_results` and `state.modules` are both empty, `estudo` routes to `classifier` first.

**Progressive immersion**: Language mix (PT-BR/EN) adapts to CEFR level (A1: 70% PT-BR → C1+: 100% EN).

**Autonomous testing**: `teacher` can propose tests when module ends, recurring errors detected, or level-up suspected.

**Continuous observation**: `estudo` tracks error patterns, saves/removes notes in student profiles automatically.

## Student profiles

Stored as JSON in `src/knowledge/students/<uuid>.json`. Managed via `src/knowledge/student_store.py`:
- `find_student(name)` / `create_student(name)` / `get_student(uuid)`
- `add_note(uuid, text, category)` / `record_success(uuid, note_id)` / `resolve_note(uuid, note_id)`
- `update_profile(uuid, **kwargs)`

## State (`LearnerState`)

- `front_scores`: 6 fronts, each 0-100
- `modules`: list of `Module` dataclasses (pending/active/completed)
- `test_results`: list of `TestResult`
- `error_patterns`: recurring errors tracked by front + pattern
- `current_module_id`: points to active module
- Helper methods: `get_weakest_front()`, `get_strongest_front()`, `get_active_module()`, `register_error()`

## PT-BR specific difficulties (hard-coded in `knowledge/`)

Top false cognates to always test: actually, pretend, library, parents, push.
Top grammatical pain points: no auxiliary in questions, missing 3rd person -s, prepositions (depend on, married to), present-perfect nonexistent in PT-BR.
Phonetic priorities: /θð/, /h/, schwa, vowel length, word stress, can/can't distinction.

## Tools

- `WebSearchTool`: defaults to `enabled=False` — offline mode uses hard-coded resource list (British Council, BBC, Cambridge, YouGlish, Forvo, EF SET, Merriam-Webster). When enabled, queries DuckDuckGo API.
- `KnowledgeBaseTool`: wraps `src/knowledge/cefr.py` and `src/knowledge/ptbr_phonetics.py` — query CEFR descriptors, phonetic difficulties, grammar difficulties.

## Model routing per agent

- `estudo`/`teacher`/`builder`: Claude Sonnet 4 (balanced)
- `classifier`: Claude Opus 4 (analytical for accurate placement)
- `coach`: Gemini 2.5 Flash (free, multimodal) — fallback to teacher/Sonnet
- `tester`/`tracker`: Claude Haiku 4 (fast, cheap)

## Agent definitions

- `.opencode/agents/*.md` — opencode format (supports `@name` subagent calls)
- `.claude/agents/*.md` — Claude Code compatibility

## No tests, no CI, no lint/formatter config

Write whatever Python is needed. There are no existing conventions to follow beyond the `AgentProtocol` shape.
