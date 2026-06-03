from __future__ import annotations
from src.agents.base import BaseAgent
from src.state import LearnerState, Front
from src.knowledge.ptbr_phonetics import PTBR_PHONETIC_DIFFICULTIES


class PhoneticCoach(BaseAgent):
    name = "coach"
    description = "Treina pronuncia com foco em dificuldades de falantes PT-BR"
    tags = ["core", "pronunciation", "phonetics", "pt-br"]

    def build_system_prompt(self) -> str:
        return (
            "Coach de pronuncia especializado em falantes PT-BR. "
            "Ensina sons problematicos: th, h aspirado, schwa, "
            "vowel length, word stress. Usa minimal pairs."
        )

    def process(self, state: LearnerState, user_input: str) -> str:
        state.add_interaction("learner", self.name, user_input)

        if "explica" in user_input.lower() or "como" in user_input.lower():
            response = self._explain(state, user_input)
        elif "pratica" in user_input.lower() or "treina" in user_input.lower():
            response = self._practice(state)
        elif "corrige" in user_input.lower():
            response = self._correct(state, user_input)
        else:
            response = self._menu(state)

        state.add_interaction("agent", self.name, response)
        return response

    def _explain(self, state: LearnerState, text: str) -> str:
        guides = {
            "th": (
                "Som /th/ (think, thanks, three)\n"
                "Erro PT-BR: substitui por /f/ ou /t/\n"
                "Como fazer: lingua entre os dentes, sopre.\n"
                "Minimal pairs: think/sink, thin/tin"
            ),
            "h": (
                "Som /h/ (house, happy)\n"
                "Erro PT-BR: omitem (portugues nao tem /h/)\n"
                "Como fazer: suspire com a boca aberta.\n"
                "Minimal pairs: heat/eat, hill/ill"
            ),
            "schwa": (
                "Schwa (about, banana, the)\n"
                "Som neutro, o mais comum do ingles.\n"
                "Erro PT-BR: pronunciam todas as vogais.\n"
                "Dica: relaxe a boca, faca 'uh'."
            ),
        }
        for key, guide in guides.items():
            if key in text.lower():
                return guide
        return "Sons disponiveis: th, h, schwa. Digite 'explica th' para aprender."

    def _practice(self, state: LearnerState) -> str:
        pairs = []
        for d in PTBR_PHONETIC_DIFFICULTIES:
            for p in d.get("minimal_pairs", []):
                pairs.append(f"  {p[0]} / {p[1]}")
        return "Minimal pairs para praticar:\n" + "\n".join(pairs[:8])

    def _correct(self, state: LearnerState, text: str) -> str:
        issues = []
        if any(w in text.lower() for w in ["think", "three", "thanks"]):
            issues.append("th: lingua entre os dentes")
        if any(w in text.lower() for w in ["house", "happy", "hello"]):
            issues.append("h: nao omita o sopro")
        if issues:
            for i in issues:
                state.register_error(Front.PRONUNCIATION, i, text[:50])
        return "Analise:\n" + "\n".join(f"  - {i}" for i in issues) if issues else "Nao detectei erros especificos."

    def _menu(self, state: LearnerState) -> str:
        return (
            "Phonetic Coach - menu:\n"
            "  'explica th' - aprender som th\n"
            "  'explica h' - aprender som h\n"
            "  'explica schwa' - aprender schwa\n"
            "  'pratica' - minimal pairs\n"
            "  'corrige <frase>' - analisar sua pronuncia"
        )
