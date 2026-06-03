from __future__ import annotations
from datetime import datetime
from typing import List, Tuple
from src.agents.base import BaseAgent
from src.state import LearnerState, CefrLevel, Front, TestResult, Module


class TestBuilder(BaseAgent):
    name = "tester"
    description = "Cria testes de nivelamento e modulares alinhados ao CEFR"
    tags = ["core", "testing", "assessment"]

    def build_system_prompt(self) -> str:
        return (
            "Criador de testes alinhados ao CEFR. "
            "Avalia gramatica, vocabulario, escrita e compreensao. "
            "Inclui dificuldades PT-BR (falsos cognatos, preposicoes)."
        )

    def process(self, state: LearnerState, user_input: str) -> str:
        state.add_interaction("learner", self.name, user_input)
        module = state.get_active_module()

        if not module:
            response = self._placement_test()
        elif "corrigir" in user_input.lower():
            response = self._grade(state, module, user_input)
        else:
            response = self._module_test(module)

        state.add_interaction("agent", self.name, response)
        return response

    def _placement_test(self) -> str:
        return (
            "TESTE DE NIVELAMENTO\n\n"
            "Grammar:\n"
            "1. She ___ a student. (am/is/are/be)\n"
            "2. I ___ like coffee. (don't/doesn't/not)\n"
            "3. What ___ you do yesterday? (did/do/does)\n\n"
            "Vocabulary:\n"
            "4. What does 'actually' mean?\n"
            "   a) atualmente  b) na verdade\n"
            "5. Opposite of 'cheap': ___\n\n"
            "Responda com o numero (ex: '1b'). "
            "Digite 'corrigir' quando terminar."
        )

    def _module_test(self, module: Module) -> str:
        return (
            f"TESTE: {module.title} (Nivel {module.cefr_level.value})\n\n"
            "1. Write 3 sentences about the module topic.\n"
            "2. Translate: 'Eu gosto de estudar ingles.'\n"
            "3. Use the grammar from this module in a sentence.\n\n"
            "Digite 'corrigir' para feedback."
        )

    def _grade(self, state: LearnerState, module: Module, text: str) -> str:
        score, feedback = self._evaluate(text)
        result = TestResult(
            test_id=f"{module.id}_{datetime.now().isoformat()}",
            module_id=module.id,
            front=module.front,
            score=score,
            max_score=100,
            errors=self._extract_errors(text),
            submitted_at=datetime.now().isoformat(),
        )
        state.test_results.append(result)
        if module.front in state.front_scores:
            state.front_scores[module.front] = max(state.front_scores[module.front], score)
        return f"Nota: {score:.0f}/100\n{feedback}"

    def _evaluate(self, text: str) -> Tuple[float, str]:
        wc = len(text.split())
        score = min(100, wc * 5)
        if score >= 80:
            fb = "Excelente!"
        elif score >= 50:
            fb = "Bom, mas pode melhorar."
        else:
            fb = "Vamos revisar este topico."
        return score, fb

    def _extract_errors(self, text: str) -> List[str]:
        errors = []
        for p in ["nao", "e ", "para"]:
            if p in text.lower():
                errors.append(f"Portugues detectado: '{p}'")
        return errors
