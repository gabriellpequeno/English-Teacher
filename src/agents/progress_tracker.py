from __future__ import annotations
from typing import Dict, List, Tuple
from collections import defaultdict
from src.agents.base import BaseAgent
from src.state import LearnerState, CefrLevel, Front


class ProgressTracker(BaseAgent):
    name = "tracker"
    description = "Monitora metricas de progresso e gera relatorios"
    tags = ["core", "analytics", "metrics"]

    def build_system_prompt(self) -> str:
        return (
            "Analista de progresso. Calcula metricas de desempenho, "
            "identifica tendencias, erros recorrentes, "
            "e fornece dados para o Module Builder ajustar o curriculo."
        )

    def process(self, state: LearnerState, user_input: str) -> str:
        state.add_interaction("learner", self.name, user_input)

        if "relatorio" in user_input.lower() or "progresso" in user_input.lower():
            response = self._report(state)
        elif "erro" in user_input.lower():
            response = self._errors(state)
        else:
            response = self._status(state)

        state.add_interaction("agent", self.name, response)
        return response

    def _report(self, state: LearnerState) -> str:
        trends = self._trends(state)
        avg = sum(t.score for t in state.test_results) / len(state.test_results) if state.test_results else 0
        completed = sum(1 for m in state.modules if m.status == "completed")

        lines = [
            f"RELATORIO DE PROGRESSO",
            f"Nivel: {state.current_level.value}",
            f"Modulos concluidos: {completed}/{len(state.modules)}",
            f"Testes: {len(state.test_results)} (media: {avg:.0f}/100)",
            f"Interacoes: {len(state.interactions)}",
            "",
            "Scores:",
        ]
        icons = {"subindo": "+", "caindo": "-", "estavel": "~"}
        for front, score in sorted(state.front_scores.items(), key=lambda x: x[1]):
            t = trends.get(front, "?")
            lines.append(f"  {front.value:15s} {score:3.0f}/100 [{icons.get(t, '?')}]")

        return "\n".join(lines)

    def _errors(self, state: LearnerState) -> str:
        if not state.error_patterns:
            return "Nenhum erro recorrente detectado ainda."
        by_front = defaultdict(int)
        for e in state.error_patterns:
            by_front[e.front] += e.frequency
        lines = ["Erros recorrentes:"]
        for front, count in sorted(by_front.items(), key=lambda x: -x[1]):
            lines.append(f"  {front.value}: {count} ocorrencias")
        return "\n".join(lines)

    def _status(self, state: LearnerState) -> str:
        return (
            f"Status: {state.current_level.value} | "
            f"Modulos: {sum(1 for m in state.modules if m.status == 'completed')}/{len(state.modules)} | "
            f"Testes: {len(state.test_results)}"
        )

    def _trends(self, state: LearnerState) -> Dict[Front, str]:
        trends = {}
        if len(state.test_results) < 2:
            return {f: "precisa de mais dados" for f in Front}
        recent = state.test_results[-3:]
        by_front = defaultdict(list)
        for r in recent:
            by_front[r.front].append(r.score)
        for f in Front:
            scores = by_front.get(f, [])
            if len(scores) >= 2:
                trends[f] = "subindo" if scores[-1] > scores[0] + 5 else "caindo" if scores[-1] < scores[0] - 5 else "estavel"
            else:
                trends[f] = "precisa de mais dados"
        return trends
