from __future__ import annotations
from datetime import datetime
from typing import Dict
from src.agents.base import BaseAgent
from src.state import LearnerState, CefrLevel, Front


class LevelClassifier(BaseAgent):
    name = "classifier"
    description = "Classifica o nivel CEFR do aluno (A1-C2)"
    tags = ["core", "assessment", "cefr"]

    def build_system_prompt(self) -> str:
        return (
            "Classificador de nivel CEFR. Entrevista o aluno em ingles, "
            "analisa gramatica, vocabulario e compreensao, "
            "e retorna o nivel A1-C2 com recomendacoes."
        )

    def process(self, state: LearnerState, user_input: str) -> str:
        state.add_interaction("learner", self.name, user_input)

        if not self._has_data(state):
            response = self._interview(state)
        else:
            result = self._classify(state, user_input)
            response = self._format(result, state)

        state.add_interaction("agent", self.name, response)
        return response

    def _has_data(self, state: LearnerState) -> bool:
        return bool(state.test_results) or any(m.status == "completed" for m in state.modules)

    def _interview(self, state: LearnerState) -> str:
        return (
            "Vou descobrir seu nivel. Responda em INGLES:\n\n"
            "1. What's your name and where are you from?\n"
            "2. How long have you been studying English?\n"
            "3. Tell me about your daily routine.\n\n"
            "Depois de responder, digite 'classificar'."
        )

    def _classify(self, state: LearnerState, text: str) -> Dict:
        self._update_scores(state, text)
        from src.knowledge.cefr import estimate_level_from_scores
        level = estimate_level_from_scores(state.front_scores)
        state.current_level = level
        return {
            "level": level,
            "weakest": state.get_weakest_front(),
            "strongest": state.get_strongest_front(),
        }

    def _update_scores(self, state: LearnerState, text: str):
        wc = len(text.split())
        errors = self._count_errors(text)
        vocab = self._estimate_vocab(text)
        state.front_scores[Front.SPEAKING] = min(100, max(state.front_scores[Front.SPEAKING], wc * 5))
        state.front_scores[Front.GRAMMAR] = max(0, 100 - errors * 15)
        state.front_scores[Front.VOCABULARY] = min(100, max(state.front_scores[Front.VOCABULARY], vocab * 25))

    def _count_errors(self, text: str) -> int:
        patterns = ["he go", "she don't", "you is", "they was", "i no"]
        return sum(1 for p in patterns if p in text.lower())

    def _estimate_vocab(self, text: str) -> int:
        b2 = ["although", "however", "therefore", "significant", "opportunity"]
        c1 = ["furthermore", "comprehensive", "phenomenon", "substantial", "inevitable"]
        tl = text.lower()
        score = 1
        if any(w in tl for w in b2):
            score = 3
        if any(w in tl for w in c1):
            score = 4
        return score

    def _format(self, result: Dict, state: LearnerState) -> str:
        lvl = result["level"]
        labels = {"A1": "Iniciante", "A2": "Basico", "B1": "Intermediario",
                  "B2": "Intermediario Superior", "C1": "Avancado", "C2": "Proficiente"}
        return (
            f"Classificacao:\n"
            f"Nivel CEFR: {lvl.value} ({labels.get(lvl.value, '')})\n"
            f"Melhor: {result['strongest'].value}\n"
            f"Foco: {result['weakest'].value}\n\n"
            f"{state.summary()}\n\n"
            "Proximo passo: Module Builder vai criar seu plano de estudos."
        )
