from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime


class CefrLevel(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

    def __lt__(self, other: "CefrLevel") -> bool:
        order = ["A1", "A2", "B1", "B2", "C1", "C2"]
        return order.index(self.value) < order.index(other.value)

    def __le__(self, other: "CefrLevel") -> bool:
        return self == other or self < other


class Front(str, Enum):
    WRITING = "writing"
    LISTENING = "listening"
    SPEAKING = "speaking"
    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    PRONUNCIATION = "pronunciation"


@dataclass
class Module:
    id: str
    title: str
    front: Front
    cefr_level: CefrLevel
    topics: List[str]
    objectives: List[str]
    status: str = "pending"  # pending, active, completed
    score: Optional[float] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class TestResult:
    test_id: str
    module_id: str
    front: Front
    score: float
    max_score: float
    errors: List[str]
    submitted_at: str


@dataclass
class ErrorPattern:
    front: Front
    pattern: str
    examples: List[str]
    frequency: int
    last_seen: str


@dataclass
class Interaction:
    role: str  # "agent" or "learner"
    agent: Optional[str]
    content: str
    timestamp: str


@dataclass
class LearnerState:
    name: str = "Aluno"
    native_language: str = "pt-BR"
    target_language: str = "en"

    current_level: CefrLevel = CefrLevel.A1
    target_level: CefrLevel = CefrLevel.B2

    front_scores: Dict[Front, float] = field(default_factory=lambda: {
        Front.WRITING: 0.0,
        Front.LISTENING: 0.0,
        Front.SPEAKING: 0.0,
        Front.GRAMMAR: 0.0,
        Front.VOCABULARY: 0.0,
        Front.PRONUNCIATION: 0.0,
    })

    modules: List[Module] = field(default_factory=list)
    test_results: List[TestResult] = field(default_factory=list)
    error_patterns: List[ErrorPattern] = field(default_factory=list)
    interactions: List[Interaction] = field(default_factory=list)
    current_module_id: Optional[str] = None
    session_start: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_weakest_front(self) -> Front:
        return min(self.front_scores, key=self.front_scores.get)

    def get_strongest_front(self) -> Front:
        return max(self.front_scores, key=self.front_scores.get)

    def get_fronts_ranking(self) -> List[Tuple[Front, float]]:
        return sorted(self.front_scores.items(), key=lambda x: x[1])

    def get_active_module(self) -> Optional[Module]:
        for m in self.modules:
            if m.id == self.current_module_id:
                return m
        return None

    def add_interaction(self, role: str, agent: Optional[str], content: str):
        self.interactions.append(Interaction(
            role=role, agent=agent,
            content=content,
            timestamp=datetime.now().isoformat()
        ))

    def register_error(self, front: Front, pattern: str, example: str):
        for ep in self.error_patterns:
            if ep.front == front and ep.pattern == pattern:
                ep.frequency += 1
                ep.last_seen = datetime.now().isoformat()
                ep.examples.append(example)
                return
        self.error_patterns.append(ErrorPattern(
            front=front, pattern=pattern,
            examples=[example], frequency=1,
            last_seen=datetime.now().isoformat()
        ))

    def summary(self) -> str:
        lines = [
            f"=== {self.name} ===",
            f"Nível CEFR: {self.current_level.value}",
            f"Língua nativa: {self.native_language}",
            f"--- Front Scores ---",
        ]
        for front, score in sorted(self.front_scores.items(), key=lambda x: x[1]):
            bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
            lines.append(f"  {front.value:15s} {bar} {score:.0f}/100")
        lines.append(f"Módulos concluídos: {sum(1 for m in self.modules if m.status == 'completed')}")
        lines.append(f"Erros recorrentes: {len(self.error_patterns)}")
        return "\n".join(lines)
