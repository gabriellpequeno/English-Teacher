from __future__ import annotations
from src.state import LearnerState
from src.registry import registry


class Orchestrator:
    """Roteador. Nao eh agente - eh consumidor do registry."""

    def route(self, state: LearnerState, user_input: str) -> str:
        state.add_interaction("learner", "orchestrator", user_input)
        agent = self._pick(state, user_input)
        if not agent:
            return "Nenhum agente disponivel. Execute init() primeiro."
        state.add_interaction("agent", agent.name, f"roteado para {agent.name}")
        return agent.process(state, user_input)

    def _pick(self, state: LearnerState, user_input: str):
        ui = user_input.lower()

        if not state.test_results and not state.modules:
            return registry.get("classifier")

        intent_map = {
            "tester": ["test", "prova", "avaliar", "quiz", "nivelamento"],
            "coach": ["th", "pronuncia", "som", "schwa", "fonet", "minimal", "treina"],
            "tracker": ["progresso", "relatorio", "desempenho", "status", "erro"],
            "builder": ["plano", "modulo", "curriculo", "proximo", "curso"],
            "teacher": ["aula", "explica", "aprender", "pratica", "como", "?"],
        }

        for agent_name, keywords in intent_map.items():
            if any(k in ui for k in keywords):
                return registry.get(agent_name)

        if state.get_active_module():
            return registry.get("teacher")

        return registry.get("teacher")

    def status(self, state: LearnerState) -> str:
        return (
            f"Orchestrator | "
            f"Registry: {registry.count()} agents | "
            f"Learner: {state.name} ({state.current_level.value}) | "
            f"Modulos: {len(state.modules)} | "
            f"Testes: {len(state.test_results)}"
        )


orchestrator = Orchestrator()
