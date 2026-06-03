"""Ponto de entrada unico (/init) para qualquer harness.

Uso:
    from src.factory import init

    agents, state = init()
    agents["teacher"].process(state, "hello")
"""

from __future__ import annotations
from typing import Dict, Optional, List, Tuple, Any
from src.state import LearnerState, CefrLevel
from src.registry import registry
from src.tools.search import WebSearchTool, KnowledgeBaseTool


def init(
    learner_name: str = "Aluno",
    target_level: str = "B2",
    web_search: bool = False,
    agents: Optional[List[str]] = None,
    scores: Optional[Dict[str, float]] = None,
) -> Tuple[Dict[str, Any], LearnerState]:
    """Inicializa o sistema. Chamada unica que qualquer harness faz.

    Args:
        learner_name: Nome do aluno.
        target_level: Nivel CEFR alvo (A1-C2).
        web_search: Ativar busca na web real.
        agents: Lista de agentes para carregar (None = todos).
        scores: Scores iniciais por front.

    Returns:
        (dict[name -> agent], LearnerState)
    """
    _validate_level(target_level)
    state = _build_state(learner_name, target_level, scores)
    tools = _build_tools(web_search)
    instances = _build_agents(tools, agents)

    registry.clear()
    for name, agent in instances.items():
        registry.register(name, agent, tags=getattr(agent, "tags", []))

    return instances, state


def init_from_config(config: dict) -> Tuple[Dict[str, Any], LearnerState]:
    """Init a partir de dicionario de configuracao."""
    return init(
        learner_name=config.get("learner_name", "Aluno"),
        target_level=config.get("target_level", "B2"),
        web_search=config.get("web_search", False),
        agents=config.get("agents"),
        scores=config.get("scores"),
    )


def _validate_level(level: str) -> None:
    valid = {l.value for l in CefrLevel}
    if level.upper() not in valid:
        raise ValueError(f"Nivel CEFR invalido: {level}. Validos: {sorted(valid)}")


def _build_state(name: str, target: str, scores: Optional[Dict[str, float]]) -> LearnerState:
    state = LearnerState(
        name=name,
        target_level=CefrLevel(target.upper()),
    )
    if scores:
        from src.state import Front
        for k, v in scores.items():
            try:
                front = Front(k)
                if front in state.front_scores:
                    state.front_scores[front] = float(v)
            except ValueError:
                pass
    return state


def _build_tools(web_search: bool) -> dict:
    return {
        "web_search": WebSearchTool(enabled=web_search),
        "knowledge_base": KnowledgeBaseTool(),
    }


def _build_agents(tools: dict, only: Optional[List[str]] = None) -> Dict[str, Any]:
    from src.agents.level_classifier import LevelClassifier
    from src.agents.module_builder import ModuleBuilder
    from src.agents.teacher import Teacher
    from src.agents.test_builder import TestBuilder
    from src.agents.progress_tracker import ProgressTracker
    from src.agents.phonetic_coach import PhoneticCoach

    all_agents = {
        "classifier": LevelClassifier(**tools),
        "builder": ModuleBuilder(**tools),
        "teacher": Teacher(**tools),
        "tester": TestBuilder(**tools),
        "tracker": ProgressTracker(**tools),
        "coach": PhoneticCoach(**tools),
    }

    if only is not None:
        return {n: a for n, a in all_agents.items() if n in only}

    return all_agents
