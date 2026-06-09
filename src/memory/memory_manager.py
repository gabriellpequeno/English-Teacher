"""Sistema de Memoria Dinamica para desenvolvimento.

Totalmente isolado dos study agents (src/agents/).
Uso:
    from src.memory import MemoryManager
    mm = MemoryManager()
    ctx = mm.get_context("implementar autenticacao")
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
from datetime import datetime
import re


MEMORY_DIR_DEFAULT = Path(__file__).resolve().parent.parent.parent / ".memory"


@dataclass
class MemoryPattern:
    id: str
    title: str
    category: str  # workflow | code | decision | technical
    status: str  # suggested | confirmed | deprecated
    confidence: str  # low | medium | high
    learned_at: str
    last_observed: str
    source: str
    description: str
    evidence: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)


SEEDS: list[dict] = [
    {
        "id": "cs-001",
        "title": "Pure stdlib — zero dependencias externas",
        "category": "code",
        "description": "Todo codigo Python usa apenas a biblioteca padrao. Nenhum pip install.",
        "evidence": ["Nao ha requirements.txt", "Nao ha pyproject.toml", "from __future__ import annotations em todo lugar"],
    },
    {
        "id": "cs-002",
        "title": "Structural subtyping com Protocol",
        "category": "code",
        "description": "Usar typing.Protocol + @runtime_checkable para definir contratos. Nao requer heranca.",
        "evidence": ["AgentProtocol em src/protocol.py", "isinstance(agent, AgentProtocol) no registry"],
    },
    {
        "id": "cs-003",
        "title": "Dataclasses para modelos de dados",
        "category": "code",
        "description": "@dataclass + field(default_factory=...) para todos os modelos de estado e config.",
        "evidence": ["LearnerState, Module, TestResult, ErrorPattern, Interaction em src/state.py"],
    },
    {
        "id": "cs-004",
        "title": "Enum(str, Enum) para valores fixos e comparaveis",
        "category": "code",
        "description": "Valores com conjunto conhecido viram Enum com str heritage para serializacao natural.",
        "evidence": ["CefrLevel com __lt__/__le__", "Front com 6 valores fixos"],
    },
    {
        "id": "cs-005",
        "title": "Tools injetadas via **kwargs em BaseAgent",
        "category": "code",
        "description": "Dependencias externas (WebSearchTool, KnowledgeBaseTool) injetadas no construtor via **kwargs.",
        "evidence": ["BaseAgent.__init__(**kwargs) em src/agents/base.py", "factory._build_agents() passa tools assim"],
    },
    {
        "id": "wf-001",
        "title": "Factory.init() como entry point unico",
        "category": "workflow",
        "description": "Todo harness (CLI, API, teste) chama factory.init() para inicializar o sistema. Nao ha init espalhado.",
        "evidence": ["src/main.py chama factory.init()", "README.md documenta factory.init() como unico entry point"],
    },
    {
        "id": "wf-002",
        "title": "Dual layer: Python agents + .md definitions",
        "category": "workflow",
        "description": "Cada agente tem implementacao Python (src/agents/) e definicao em markdown (.opencode/agents/ e .claude/agents/).",
        "evidence": ["8 agentes Python + 8 definicoes .opencode + 8 definicoes .claude"],
    },
    {
        "id": "wf-003",
        "title": "Interacoes logadas em LearnerState",
        "category": "workflow",
        "description": "Toda interacao agente/learner e registrada em state.interactions com timestamp.",
        "evidence": ["state.add_interaction() chamado no orchestrator e em cada agent.process()"],
    },
    {
        "id": "dec-001",
        "title": "Conhecimento separado da logica dos agentes",
        "category": "decision",
        "description": "Dados de dominio (CEFR, fonetica PT-BR) ficam em src/knowledge/, agentes em src/agents/. Agentes consultam via KnowledgeBaseTool.",
        "evidence": ["src/knowledge/cefr.py e ptbr_phonetics.py sao dados puros", "KnowledgeBaseTool faz a ponte"],
    },
    {
        "id": "dec-002",
        "title": "Roteamento Python por keywords, roteamento AI por @mentions",
        "category": "decision",
        "description": "Python layer usa intent_map com palavras-chave. AI layer (opencode/Claude) usa @nome nos prompts .md. Nao misturar.",
        "evidence": ["Orchestrator._pick() com intent_map", "estudo.md chama subagents com @classifier, @teacher etc"],
    },
]


class MemoryManager:
    """Gerencia padroes aprendidos do time de desenvolvimento.

    Leitura e escrita em .memory/*.md.
    Totalmente isolado — study agents nunca acessam.
    """

    def __init__(self, memory_dir: str | Path = MEMORY_DIR_DEFAULT):
        self._dir = Path(memory_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self.patterns: dict[str, MemoryPattern] = {}
        self._load()

    # ----------------------------------------------------------------
    # Leitura
    # ----------------------------------------------------------------

    def get_context(self, task_description: str) -> str:
        """Retorna markdown com padroes relevantes para a task."""
        relevant = self.find(task_description)
        if not relevant:
            return ""

        lines = ["--- Padroes do Projeto (auto-aprendidos) ---"]
        for p in relevant:
            status_icon = "[OK]" if p.status == "confirmed" else "[?]" if p.status == "suggested" else "[--]"
            lines.append(f"{status_icon} [{p.id}] {p.title} ({p.category}, {p.confidence})")
        return "\n".join(lines)

    def find(self, query: str, category: str | None = None) -> list[MemoryPattern]:
        """Busca padroes por correspondencia no titulo, descricao ou evidence."""
        q = query.lower()
        result = []
        for p in self.patterns.values():
            if category and p.category != category:
                continue
            if p.status == "deprecated":
                continue
            if (
                q in p.title.lower()
                or q in p.description.lower()
                or any(q in e.lower() for e in p.evidence)
                or q in p.id.lower()
            ):
                result.append(p)
        return result

    def list_suggested(self) -> list[MemoryPattern]:
        """Padroes aguardando confirmacao do usuario."""
        return [p for p in self.patterns.values() if p.status == "suggested"]

    def list_by_category(self, category: str) -> list[MemoryPattern]:
        return [p for p in self.patterns.values() if p.category == category]

    def get(self, pattern_id: str) -> MemoryPattern | None:
        return self.patterns.get(pattern_id)

    # ----------------------------------------------------------------
    # Escrita
    # ----------------------------------------------------------------

    def suggest(
        self,
        title: str,
        category: str,
        description: str,
        source: str = "",
        evidence: list[str] | None = None,
    ) -> MemoryPattern:
        """Registra um novo padrao como 'suggested' — precisa de confirmacao."""
        existing = self._find_duplicate(title)
        if existing:
            return existing

        pattern_id = self._next_id(category)
        now = datetime.now().isoformat()
        pattern = MemoryPattern(
            id=pattern_id,
            title=title,
            category=category,
            status="suggested",
            confidence="medium",
            learned_at=now,
            last_observed=now,
            source=source,
            description=description,
            evidence=evidence or [],
        )
        self.patterns[pattern_id] = pattern
        self._save()
        return pattern

    def confirm(self, pattern_id: str) -> MemoryPattern | None:
        """Usuario confirmou o padrao."""
        p = self.patterns.get(pattern_id)
        if not p:
            return None
        p.status = "confirmed"
        p.last_observed = datetime.now().isoformat()
        self._save()
        return p

    def reject(self, pattern_id: str) -> MemoryPattern | None:
        """Usuario rejeitou — marca como deprecated."""
        p = self.patterns.get(pattern_id)
        if not p:
            return None
        p.status = "deprecated"
        self._save()
        return p

    def record_application(self, pattern_id: str) -> None:
        """Atualiza last_observed quando padrao e aplicado."""
        p = self.patterns.get(pattern_id)
        if p:
            p.last_observed = datetime.now().isoformat()
            self._save()

    # ----------------------------------------------------------------
    # Manutencao
    # ----------------------------------------------------------------

    def refresh(self) -> None:
        """Recarrega todos os .md do disco."""
        self.patterns.clear()
        self._load()

    def optimize(self) -> list[str]:
        """Se alguma categoria tem 3+ padroes confirmados, faz split em arquivo dedicado.

        Returns:
            Lista de nomes de arquivos criados.
        """
        created = []
        for cat in ["workflow", "code", "decision", "technical"]:
            cat_patterns = [
                p for p in self.patterns.values()
                if p.category == cat and p.status == "confirmed"
            ]
            if len(cat_patterns) >= 3:
                filename = f"{cat}.md"
                filepath = self._dir / filename
                if self._write_category_file(filepath, cat, cat_patterns):
                    created.append(filename)

        self._cleanup_generic()
        return created

    # ----------------------------------------------------------------
    # Serializacao interna
    # ----------------------------------------------------------------

    def _load(self) -> None:
        """Carrega todos os .md do diretorio de memoria."""
        has_pattern_files = any(
            f.name not in ("README.md", "AGENTS.md") and f.suffix == ".md"
            for f in self._dir.iterdir()
        ) if self._dir.exists() else False

        if not has_pattern_files:
            self._write_seeds()

        for fp in sorted(self._dir.glob("*.md")):
            if fp.name in ("README.md", "AGENTS.md"):
                continue
            self._load_file(fp)

    def _load_file(self, filepath: Path) -> None:
        """Parseia um arquivo .md e extrai padroes."""
        content = filepath.read_text(encoding="utf-8")
        # Remove frontmatter (YAML entre ---)
        body = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL)

        # Extrai secoes de padrao (## id: Title)
        sections = re.split(r"\n(?=## )", body)
        for section in sections:
            pattern = self._parse_pattern_section(section)
            if pattern:
                self.patterns[pattern.id] = pattern

    def _parse_pattern_section(self, text: str) -> MemoryPattern | None:
        """Parseia uma secao '## id: Title' em um MemoryPattern."""
        match = re.match(r"## (\S+): (.+)\n", text)
        if not match:
            return None

        pattern_id = match.group(1)
        title = match.group(2).strip()

        # Extrai bullets de metadata
        status = "suggested"
        confidence = "medium"
        category = "technical"
        learned_at = ""
        source = ""
        evidence: list[str] = []
        related: list[str] = []

        for bullet_match in re.finditer(r"^- \*\*(\w+)\*\*: (.+)$", text, re.MULTILINE):
            key = bullet_match.group(1).lower()
            val = bullet_match.group(2).strip()
            if key == "status":
                status = val
            elif key == "confidence":
                confidence = val
            elif key == "category":
                category = val
            elif key == "learned":
                learned_at = val
            elif key == "source":
                source = val

        # Evidence section
        ev_section = re.search(r"### Evidence\n((?:- .+\n?)+)", text)
        if ev_section:
            evidence = re.findall(r"- (.+)", ev_section.group(1))

        # Related section
        rel_section = re.search(r"### Related\n((?:- .+\n?)+)", text)
        if rel_section:
            related = re.findall(r"- \[\[(.+?)\]\]", rel_section.group(1))

        # Description: texto apos o ultimo metadata bullet ate o proximo ###
        lines = text.split("\n")
        in_bullets = True
        desc_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## "):
                continue
            if in_bullets:
                if stripped.startswith("- **"):
                    continue
                if stripped == "":
                    continue
                in_bullets = False
            if stripped.startswith("### "):
                break
            if stripped or desc_lines:  # captura linhas vazias no meio da descricao
                desc_lines.append(line)
        description = "\n".join(desc_lines).strip()

        return MemoryPattern(
            id=pattern_id,
            title=title,
            category=category,
            status=status,
            confidence=confidence,
            learned_at=learned_at or datetime.now().isoformat(),
            last_observed=datetime.now().isoformat(),
            source=source,
            description=description,
            evidence=evidence,
            related=related,
        )

    def _save(self) -> None:
        """Salva todos os padroes no arquivo patterns.md."""
        # Agrupa por arquivo (categorias que ja tem arquivo dedicado)
        by_file: dict[str, list[MemoryPattern]] = {}
        for p in self.patterns.values():
            target = self._file_for_pattern(p)
            by_file.setdefault(target, []).append(p)

        for filename, patterns in by_file.items():
            filepath = self._dir / filename
            self._write_pattern_file(filepath, patterns)

    def _file_for_pattern(self, pattern: MemoryPattern) -> str:
        """Determina em qual arquivo o padrao deve ficar."""
        cat_map = {"workflow": "workflow.md", "code": "code.md",
                    "decision": "decisions.md", "technical": "technical.md"}
        dedicated = cat_map.get(pattern.category)
        if dedicated and (self._dir / dedicated).exists():
            return dedicated
        return "patterns.md"

    def _write_pattern_file(self, filepath: Path, patterns: list[MemoryPattern]) -> None:
        """Escreve padroes em um arquivo .md com frontmatter."""
        patterns.sort(key=lambda p: p.id)
        now = datetime.now().strftime("%Y-%m-%d")
        category_names = {
            "workflow": "Workflow",
            "code": "Código",
            "decision": "Decisões Arquiteturais",
            "technical": "Técnicos",
        }
        cat = patterns[0].category if patterns else "technical"
        title = category_names.get(cat, "Padrões")

        lines = [
            "---",
            f"updated: {now}",
            f"category: {cat}",
            f"count: {len(patterns)}",
            "---",
            "",
            f"# {title}",
            "",
            "> Aprendidos automaticamente e confirmados pelo time.",
            "",
        ]

        for p in patterns:
            lines.extend(self._format_pattern(p))
            lines.append("")

        filepath.write_text("\n".join(lines), encoding="utf-8")

    def _format_pattern(self, p: MemoryPattern) -> list[str]:
        """Formata um padrao como secao markdown."""
        lines = [
            f"## {p.id}: {p.title}",
            f"- **Status**: {p.status}",
            f"- **Confidence**: {p.confidence}",
            f"- **Category**: {p.category}",
            f"- **Learned**: {p.learned_at[:10] if p.learned_at else ''}",
            f"- **Source**: {p.source or ''}",
        ]
        if p.description:
            lines.extend(["", p.description])
        if p.evidence:
            lines.append("")
            lines.append("### Evidence")
            lines.extend(f"- {e}" for e in p.evidence)
        if p.related:
            lines.append("")
            lines.append("### Related")
            lines.extend(f"- [[{r}]]" for r in p.related)
        return lines

    # ----------------------------------------------------------------
    # Seeds
    # ----------------------------------------------------------------

    def _write_seeds(self) -> None:
        """Escreve padroes iniciais no disco (primeira execucao)."""
        patterns = []
        for data in SEEDS:
            now = datetime.now()
            p = MemoryPattern(
                id=data["id"],
                title=data["title"],
                category=data["category"],
                status="confirmed",
                confidence="high",
                learned_at=now.isoformat(),
                last_observed=now.isoformat(),
                source="Analise inicial do codigo existente",
                description=data["description"],
                evidence=data.get("evidence", []),
                related=[],
            )
            patterns.append(p)
            self.patterns[p.id] = p

        self._write_pattern_file(self._dir / "patterns.md", patterns)

    def _write_category_file(self, filepath: Path, category: str,
                              patterns: list[MemoryPattern]) -> bool:
        """Escreve arquivo dedicado para uma categoria."""
        if filepath.exists():
            return False
        self._write_pattern_file(filepath, patterns)
        return True

    def _cleanup_generic(self) -> None:
        """Remove de patterns.md os padroes que migraram para arquivos dedicados."""
        patterns_path = self._dir / "patterns.md"
        if not patterns_path.exists():
            return

        generic = [p for p in self.patterns.values()
                   if self._file_for_pattern(p) == "patterns.md"]
        if generic:
            self._write_pattern_file(patterns_path, generic)
        else:
            patterns_path.unlink(missing_ok=True)

    # ----------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------

    def _next_id(self, category: str) -> str:
        """Gera proximo ID disponivel para a categoria."""
        prefix_map = {"workflow": "wf", "code": "cs", "decision": "dec", "technical": "pt"}
        prefix = prefix_map.get(category, "pt")
        existing = [p for p in self.patterns.values() if p.id.startswith(prefix)]
        nums = [int(p.id.split("-")[1]) for p in existing if "-" in p.id]
        next_num = max(nums) + 1 if nums else (len([p for p in self.patterns.values()
                                                     if p.category == category]) + 1)
        return f"{prefix}-{next_num:03d}"

    def _find_duplicate(self, title: str) -> MemoryPattern | None:
        t = title.lower().strip()
        for p in self.patterns.values():
            if p.title.lower().strip() == t:
                return p
        return None
