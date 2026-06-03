from __future__ import annotations
from src.agents.base import BaseAgent
from src.state import LearnerState, Front, Module
from src.knowledge.cefr import get_descriptors


class Teacher(BaseAgent):
    name = "teacher"
    description = "Professor que guia o aprendizado com explicacoes e exercicios"
    tags = ["core", "teaching", "feedback"]

    def build_system_prompt(self) -> str:
        return (
            "Professor de ingles especializado em falantes PT-BR. "
            "Explica conceitos, faz perguntas, corrige com feedback construtivo."
        )

    def process(self, state: LearnerState, user_input: str) -> str:
        state.add_interaction("learner", self.name, user_input)
        module = state.get_active_module()

        if not module:
            response = "Nenhum modulo ativo. Crie um plano primeiro."
        elif user_input.lower() in ("sim", "ok", "vamos", "aula"):
            response = self._start_lesson(state, module)
        elif "explica" in user_input.lower() or "como" in user_input.lower() or "?" in user_input:
            response = self._explain(state, module, user_input)
        else:
            response = self._respond(state, module, user_input)

        state.add_interaction("agent", self.name, response)
        return response

    def _start_lesson(self, state: LearnerState, module: Module) -> str:
        descs = get_descriptors(module.cefr_level, module.front)
        return (
            f"Aula: {module.title} (Nivel {module.cefr_level.value})\n\n"
            "Objetivos:\n"
            + "\n".join(f"  - {d}" for d in descs[:3]) +
            "\n\nVamos comecar com um aquecimento:\n"
            + self._warmup(module.front)
        )

    def _warmup(self, front: Front) -> str:
        prompts = {
            Front.WRITING: "Write 3 sentences about what you did today.",
            Front.LISTENING: "Repeat: 'The weather is beautiful today.'",
            Front.SPEAKING: "Tell me about your weekend.",
            Front.GRAMMAR: "Complete: 'She ___ (go) to school every day.'",
            Front.VOCABULARY: "Name 5 objects you can see right now.",
            Front.PRONUNCIATION: "Repeat: 'I think this is the best thing.'",
        }
        return prompts.get(front, "What would you like to learn?")

    def _explain(self, state: LearnerState, module: Module, question: str) -> str:
        return (
            f"Vou explicar de forma simples.\n\n"
            f"Modulo: {module.title}\n"
            f"Foco: {module.front.value}\n\n"
            "Dicas para PT-BR:\n"
            "  - Nao traduza palavra por palavra\n"
            "  - Pense em ingles desde o inicio\n"
            "  - Comece com frases curtas\n\n"
            "Que parte especifica voce quer entender melhor?"
        )

    def _respond(self, state: LearnerState, module: Module, text: str) -> str:
        wc = len(text.split())
        ptbr = sum(1 for w in ["e", "nao", "para", "como"] if w in text.lower().split())
        feedback = "Continue praticando!"

        if ptbr > 3:
            feedback += " Tente responder em ingles."

        if wc < 5:
            feedback += " Tente desenvolver mais sua resposta."

        return feedback
