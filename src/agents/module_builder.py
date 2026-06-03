from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from src.agents.base import BaseAgent
from src.state import LearnerState, CefrLevel, Front, Module
from src.knowledge.cefr import get_descriptors


class ModuleBuilder(BaseAgent):
    name = "builder"
    description = "Constroi curriculo personalizado baseado no nivel e desempenho"
    tags = ["core", "curriculum", "adaptive"]

    def build_system_prompt(self) -> str:
        return (
            "Arquiteto de curriculo. Cria modulos de aprendizado "
            "sequenciais baseados no nivel CEFR, fronts mais fracos, "
            "e dificuldades especificas de falantes PT-BR."
        )

    def process(self, state: LearnerState, user_input: str) -> str:
        state.add_interaction("learner", self.name, user_input)

        if not state.modules:
            modules = self._build(state)
        else:
            modules = self._rebuild(state)

        response = self._format(modules, state)
        state.add_interaction("agent", self.name, response)
        return response

    def _build(self, state: LearnerState) -> List[Module]:
        level = state.current_level
        weakest = state.get_weakest_front()
        strongest = state.get_strongest_front()

        topics = {
            CefrLevel.A1: [
                ("Introductions & Greetings", Front.WRITING),
                ("Numbers & Alphabet", Front.SPEAKING),
                ("Personal Information", Front.LISTENING),
            ],
            CefrLevel.A2: [
                ("Daily Routine", Front.WRITING),
                ("Shopping & Prices", Front.LISTENING),
                ("Describing People", Front.SPEAKING),
            ],
            CefrLevel.B1: [
                ("Travel & Directions", Front.LISTENING),
                ("Opinions & Arguments", Front.WRITING),
                ("Narrating Experiences", Front.SPEAKING),
            ],
            CefrLevel.B2: [
                ("News & Current Events", Front.LISTENING),
                ("Formal Writing", Front.WRITING),
                ("Debate & Discussion", Front.SPEAKING),
            ],
            CefrLevel.C1: [
                ("Academic Writing", Front.WRITING),
                ("Advanced Listening", Front.LISTENING),
                ("Persuasive Speaking", Front.SPEAKING),
            ],
            CefrLevel.C2: [
                ("Professional Communication", Front.WRITING),
                ("Nuance & Subtlety", Front.SPEAKING),
                ("Complex Audio Analysis", Front.LISTENING),
            ],
        }

        modules = []
        for i, (title, front) in enumerate(topics.get(level, topics[CefrLevel.A1])):
            descs = get_descriptors(level, front)
            module = Module(
                id=f"{level.value}_{i+1}",
                title=title,
                front=front,
                cefr_level=level,
                topics=[title],
                objectives=descs[:3] if descs else [f"Desenvolver {front.value}"],
                status="active" if i == 0 else "pending",
            )
            modules.append(module)

        if modules:
            state.current_module_id = modules[0].id
        state.modules.extend(modules)
        return modules

    def _rebuild(self, state: LearnerState) -> List[Module]:
        pending = [m for m in state.modules if m.status == "pending"]
        if pending:
            return state.modules

        weakest = state.get_weakest_front()
        next_level = self._next_level(state)
        module = Module(
            id=f"{next_level.value}_{len(state.modules) + 1}",
            title=f"{weakest.value.title()} - {next_level.value}",
            front=weakest,
            cefr_level=next_level,
            topics=[f"{weakest.value} practice"],
            objectives=[f"Melhorar {weakest.value} para nivel {next_level.value}"],
            status="active",
        )
        state.modules.append(module)
        state.current_module_id = module.id
        return [module]

    def _next_level(self, state: LearnerState) -> CefrLevel:
        avg = sum(state.front_scores.values()) / len(state.front_scores)
        if avg >= 90 and state.current_level.value < "C2":
            return CefrLevel.C2
        if avg >= 75 and state.current_level.value < "C1":
            return CefrLevel.C1
        if avg >= 60 and state.current_level.value < "B2":
            return CefrLevel.B2
        if avg >= 45 and state.current_level.value < "B1":
            return CefrLevel.B1
        if avg >= 25 and state.current_level.value < "A2":
            return CefrLevel.A2
        return state.current_level

    def _format(self, modules: List[Module], state: LearnerState) -> str:
        lines = [f"Plano de Estudos - Nivel {state.current_level.value}\n"]
        icons = {"active": ">", "completed": "X", "pending": " "}
        for m in modules:
            lines.append(f"[{icons.get(m.status, ' ')}] {m.title} ({m.front.value})")
        lines.append(f"\n{len(modules)} modulos planejados.")
        lines.append("Digite 'aula' para comecar o primeiro modulo.")
        return "\n".join(lines)
