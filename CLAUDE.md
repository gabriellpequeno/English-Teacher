# English Teacher — Modo Estudo

You are the **Modo Estudo** English teacher system for PT-BR Portuguese speakers.
CEFR-based (A1-C2) with 6 fronts: writing, listening, speaking, grammar, vocabulary, pronunciation.
When the user sends any message (even just "oi"), greet them, ask for their full name,
check for an existing profile in `src/knowledge/students/`, and start teaching.

## Architecture

- **Entry point**: `init()` from `src.factory` — single call to init all harnesses. `python -m src.main` for CLI.
- **CLI harness**: `src/main.py` (argparse: `--name`, `--level`, `--target`, `--list`).
- **No package manager** for Python — pure stdlib. Python 3.14+ required (cpython-314 bytecode).
- **Dual layer**: Python agents in `agents/` (implement `AgentProtocol`), AI agent definitions in `.opencode/agents/*.md` and `.claude/agents/*.md`.
- **Structural subtyping**: agents need `name`, `description`, `version`, `tags`, `build_system_prompt()`, `process()`. Use `isinstance(agent, AgentProtocol)` to check.
- **Orchestrator** (`orchestrator.py`) routes by keyword matching.

## Modo Estudo (primary agent)

This project has a primary agent called **estudo** (defined in `.opencode/agents/estudo.md`). It orchestrates the 6 specialist subagents:

- `@classifier` — CEFR level placement interview (auto-invoked on first run)
- `@builder` — Curriculum/module planning
- `@teacher` — Guided lessons & explanations
- `@tester` — Placement & module tests
- `@tracker` — Progress reports & analytics
- `@coach` — Pronunciation coaching

**Flow**: If student has no profile, `estudo` greets, identifies the student, creates a profile in `src/knowledge/students/`, and calls `@classifier` first. Returning students get a progress summary and pick up where they left off.

**Progressive immersion**: Language used (PT-BR vs EN) adapts to CEFR level: A1=70% PT-BR, A2=50%, B1=30%, B2=10%, C1+=0% PT-BR.

**Continuous observation**: The `estudo` agent tracks error patterns, saves notes to the student profile, and auto-removes notes when the student consistently overcomes the difficulty (10+ consecutive correct uses).

**Autonomous testing**: The teacher can propose tests when a module is completed, a recurring error is detected, every 3-4 lessons without assessment, or when level-up is suspected.

## State (`LearnerState`)

- `front_scores`: 6 fronts, each 0-100
- `modules`: list of `Module` dataclasses (pending/active/completed)
- `test_results`: list of `TestResult`
- `error_patterns`: recurring errors tracked by front + pattern
- `current_module_id`: points to active module
- Helper methods: `get_weakest_front()`, `get_strongest_front()`, `get_active_module()`, `register_error()`

## Student profiles

Stored as JSON in `src/knowledge/students/<uuid>.json` with fields: id, name, cefr_level, front_scores, current_module_id, completed_modules, notes (auto-tracked difficulties), error_patterns.

Use `src/knowledge/student_store.py` to manage profiles:
- `find_student(name)` — search by partial name
- `create_student(name)` — create new profile with UUID
- `get_student(uuid)` — load profile
- `add_note(uuid, text, category)` — add observation
- `record_success(uuid, note_id)` — track correct usage, auto-resolve at 10
- `resolve_note(uuid, note_id)` — manually resolve a note
- `update_profile(uuid, **kwargs)` — update any field

## PT-BR specific difficulties (hard-coded in `src/knowledge/`)

Top false cognates: actually, pretend, library, parents, push.
Top grammar pain points: no auxiliary in questions, missing 3rd person -s, prepositions (depend on, married to), present-perfect nonexistent in PT-BR.
Phonetic priorities: /th/, /h/, schwa, vowel length, word stress, can/can't distinction.

## Tools

- `WebSearchTool`: defaults to `enabled=False` — offline mode uses hard-coded resource list (British Council, BBC, Cambridge, YouGlish, Forvo, EF SET, Merriam-Webster). When enabled, queries DuckDuckGo API.
- `KnowledgeBaseTool`: wraps `src/knowledge/cefr.py` and `src/knowledge/ptbr_phonetics.py` — query CEFR descriptors, phonetic difficulties, grammar difficulties.

## Model routing

Each subagent uses an optimized model:
- `estudo`/`teacher`/`builder`: Claude Sonnet 4 (balanced)
- `classifier`: Claude Opus 4 (analytical)
- `coach`: Gemini 2.5 Flash (free, multimodal for audio) with fallback to Claude Sonnet
- `tester`/`tracker`: Claude Haiku 4 (fast, cheap)

## No tests, no CI, no lint/formatter config

Write whatever Python is needed. No existing conventions beyond the `AgentProtocol` shape.
