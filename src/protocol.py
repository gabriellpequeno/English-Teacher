from __future__ import annotations
from typing import Protocol, Dict, Any, runtime_checkable


@runtime_checkable
class AgentProtocol(Protocol):
    """Protocolo minimo que qualquer agente deve seguir.

    Nao requer heranca - basta ter os atributos e metodos.
    Use isinstance(agent, AgentProtocol) para verificar.
    """

    name: str
    description: str
    version: str = "1.0.0"
    tags: list = []

    def build_system_prompt(self) -> str:
        ...

    def process(self, state: Any, user_input: str) -> str:
        ...

    def get_meta(self) -> Dict[str, Any]:
        return {
            "name": getattr(self, "name", "unknown"),
            "description": getattr(self, "description", ""),
            "version": getattr(self, "version", "1.0.0"),
            "tags": getattr(self, "tags", []),
            "type": type(self).__name__,
            "module": type(self).__module__,
        }
