from __future__ import annotations
from typing import Optional, Dict, Any
from src.protocol import AgentProtocol


class BaseAgent:
    """Mixin concreta. Nao obrigatoria - apenas evita duplicacao de codigo.

    Uso:
        class MeuAgente(BaseAgent):
            name = "meu_agente"
            description = "..."
            tags = ["tag1"]

            def build_system_prompt(self) -> str: ...
            def process(self, state, user_input) -> str: ...
    """

    name: str = "unknown"
    description: str = ""
    version: str = "1.0.0"
    tags: list = []

    def __init__(self, **kwargs):
        self.web_search = kwargs.get("web_search")
        self.knowledge_base = kwargs.get("knowledge_base")
        self.system_prompt = self.build_system_prompt()

    def build_system_prompt(self) -> str:
        return f"{self.name}: {self.description}"

    def get_meta(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "tags": self.tags,
            "type": type(self).__name__,
            "module": type(self).__module__,
        }
