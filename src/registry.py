from __future__ import annotations
from typing import Dict, Optional, List, Tuple
from src.protocol import AgentProtocol


class AgentRegistry:
    """Registry central. Harness consulta, agentes se registram."""

    def __init__(self):
        self._agents: Dict[str, AgentProtocol] = {}

    def register(self, name: str, agent: AgentProtocol, tags: Optional[List[str]] = None) -> None:
        self._agents[name] = agent

    def deregister(self, name: str) -> None:
        self._agents.pop(name, None)

    def get(self, name: str) -> Optional[AgentProtocol]:
        return self._agents.get(name)

    def list(self) -> List[Tuple[str, AgentProtocol]]:
        return list(self._agents.items())

    def list_meta(self) -> Dict[str, dict]:
        return {n: a.get_meta() for n, a in self._agents.items()}

    def list_by_tag(self, tag: str) -> List[Tuple[str, AgentProtocol]]:
        return [(n, a) for n, a in self._agents.items() if tag in getattr(a, "tags", [])]

    def count(self) -> int:
        return len(self._agents)

    def clear(self) -> None:
        self._agents.clear()

    def __contains__(self, name: str) -> bool:
        return name in self._agents

    def __getitem__(self, name: str) -> AgentProtocol:
        agent = self.get(name)
        if agent is None:
            raise KeyError(f"Agent '{name}' not found")
        return agent

    def __repr__(self) -> str:
        return f"AgentRegistry({len(self._agents)} agents: {list(self._agents.keys())})"


registry = AgentRegistry()
