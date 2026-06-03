"""Gerador de material de estudo — reforco (modulo atual) ou preview (proximo modulo).

Salva em study_materials/{level}.{num}-{topic-slug}/reforco.md ou preview.md.
"""

from __future__ import annotations
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from src.agents.base import BaseAgent
from src.state import LearnerState, CefrLevel, Front, Module, TestResult
from src.knowledge.cefr import get_descriptors
from src.knowledge.ptbr_phonetics import get_difficulties_by_level, get_grammar_difficulties


STUDY_MATERIALS_DIR = Path(__file__).resolve().parent.parent.parent / "study_materials"


class StudyGuide(BaseAgent):
    name = "material"
    description = "Gera material de estudo: reforco ou preview de modulos"
    version = "1.0.0"
    tags = ["core", "study", "materials"]

    def build_system_prompt(self) -> str:
        return (
            "Gerador de material de estudo personalizado para falantes PT-BR. "
            "Cria guias de reforco (revisao do modulo atual) e preview "
            "(previa do proximo modulo) com topicos, pesquisas, dicas e recomendacoes."
        )

    def process(self, state: LearnerState, user_input: str) -> str:
        state.add_interaction("learner", self.name, user_input)

        # Find the most recent test result
        if not state.test_results:
            response = "Nenhum teste encontrado ainda. Complete um teste primeiro."
            state.add_interaction("agent", self.name, response)
            return response

        last_test = state.test_results[-1]

        # Find the module that was tested
        tested_module = None
        for m in state.modules:
            if m.id == last_test.module_id:
                tested_module = m
                break

        if not tested_module:
            response = "Modulo do teste nao encontrado."
            state.add_interaction("agent", self.name, response)
            return response

        score_pct = last_test.score / last_test.max_score * 100

        # Determine user intent from input
        ui = user_input.lower()
        want_reforco = any(w in ui for w in ["reforco", "ref", "revisao", "revisar", "review", "atual", "esse"])
        want_preview = any(w in ui for w in ["preview", "previo", "proximo", "next", "avancar", "adiante"])

        results = []

        # Auto-detect: score < 70 -> reforco, >= 70 -> preview
        if not want_reforco and not want_preview:
            if score_pct < 70:
                want_reforco = True
            else:
                want_preview = True

        if want_reforco:
            path = self._generate_reforco(tested_module, last_test, state)
            if path:
                results.append(f"📖 Reforco gerado: {path}")
            else:
                results.append("Nao foi possivel gerar o material de reforco.")

        if want_preview:
            next_module = self._get_next_module(state, tested_module)
            if next_module:
                path = self._generate_preview(next_module, state)
                if path:
                    results.append(f"🔍 Preview gerado: {path}")
                else:
                    results.append("Nao foi possivel gerar o preview.")
            else:
                # Maybe level up?
                next_level = self._next_level(state)
                if next_level and next_level != state.current_level:
                    results.append(
                        f"Parabens! Voce esta pronto para {next_level.value}! "
                        "Use @builder para montar os proximos modulos."
                    )
                else:
                    results.append(
                        "Voce concluiu todos os modulos disponiveis! "
                        "Use @builder para gerar novos modulos."
                    )

        if not results:
            results.append("Nada foi gerado. Especifique 'reforco' ou 'preview'.")

        response = "\n\n".join(results)
        state.add_interaction("agent", self.name, response)
        return response

    # ------------------------------------------------------------------ #
    #  Reforco
    # ------------------------------------------------------------------ #

    def _generate_reforco(self, module: Module, test: TestResult, state: LearnerState) -> Optional[str]:
        """Generate reforco.md for the given module."""
        slug = self._slugify(module.title)
        folder_name = f"{module.cefr_level.value}.{module.id.split('_')[-1]}-{slug}"
        folder = STUDY_MATERIALS_DIR / folder_name
        folder.mkdir(parents=True, exist_ok=True)

        content = self._build_reforco_content(module, test, state)
        path = folder / "reforco.md"
        path.write_text(content, encoding="utf-8")
        return str(path)

    def _build_reforco_content(self, module: Module, test: TestResult, state: LearnerState) -> str:
        descs = get_descriptors(module.cefr_level, module.front)
        difficulties = get_difficulties_by_level(module.cefr_level)
        grammar = get_grammar_difficulties(module.cefr_level)
        score_pct = test.score / test.max_score * 100

        lines = [
            f"# Guia de Reforco: {module.title}",
            f"**Nivel:** {module.cefr_level.value}  **Front:** {module.front.value}",
            f"**Nota no teste:** {score_pct:.0f}/100",
            "",
            "---",
            "",
            "## 📚 Topicos para Revisar",
            "",
        ]

        if descs:
            for d in descs:
                lines.append(f"- **{d}**")
        lines.extend([
            "",
            "### Principais Dificuldades (PT-BR)",
            "",
        ])
        if difficulties:
            for diff in difficulties[:5]:
                lines.append(f"- {diff}")
        if grammar:
            for g in grammar[:5]:
                lines.append(f"- {g}")
        if test.errors:
            lines.extend([
                "",
                "### Erros no Teste",
            ])
            for err in test.errors:
                lines.append(f"- ⚠️ {err}")

        lines.extend([
            "",
            "---",
            "",
            "## 🔍 O que e Onde Pesquisar",
            "",
            f"- **\"[topic] {module.cefr_level.value} exercises\"** no Google → British Council, Cambridge English",
            f"- **\"[topic] {module.cefr_level.value} grammar\"** no YouTube → procura canais como English with Lucy, BBC Learning English",
            f"- **Pronuncia:** busque palavras-chave no YouGlish (youglish.com) e Forvo (forvo.com)",
            "- **Gramatica:** consulte o site Perfect English Grammar (perfect-english-grammar.com)",
            "",
            "---",
            "",
            "## 💡 Dicas Praticas",
            "",
            self._ptbr_tips(module.front),
            "",
            "---",
            "",
            "## 🎬 Conteudo Recomendado",
            "",
            self._recommended_content(module.cefr_level, module.front, module.title),
            "",
            "---",
            "",
            f"_Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}_",
        ])
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  Preview
    # ------------------------------------------------------------------ #

    def _generate_preview(self, module: Module, state: LearnerState) -> Optional[str]:
        """Generate preview.md for the given module."""
        slug = self._slugify(module.title)
        folder_name = f"{module.cefr_level.value}.{module.id.split('_')[-1]}-{slug}"
        folder = STUDY_MATERIALS_DIR / folder_name
        folder.mkdir(parents=True, exist_ok=True)

        content = self._build_preview_content(module, state)
        path = folder / "preview.md"
        path.write_text(content, encoding="utf-8")
        return str(path)

    def _build_preview_content(self, module: Module, state: LearnerState) -> str:
        descs = get_descriptors(module.cefr_level, module.front)
        difficulties = get_difficulties_by_level(module.cefr_level)
        grammar = get_grammar_difficulties(module.cefr_level)

        lines = [
            f"# Preview: {module.title}",
            f"**Nivel:** {module.cefr_level.value}  **Front:** {module.front.value}",
            "",
            "---",
            "",
            "## 🎯 Objetivos",
            "",
        ]
        if module.objectives:
            for obj in module.objectives:
                lines.append(f"- {obj}")
        else:
            lines.append("- Desenvolver competencias no nivel " + module.cefr_level.value)

        lines.extend([
            "",
            "## 📚 O que Voce Vai Aprender",
            "",
        ])
        if descs:
            for d in descs:
                lines.append(f"- {d}")

        lines.extend([
            "",
            "## ⚠️ Armadilhas Comuns (PT-BR)",
            "",
        ])
        if grammar:
            lines.append("**Gramatica:**")
            for g in grammar[:4]:
                lines.append(f"- {g}")
        if difficulties:
            lines.append("**Pronuncia:**")
            for diff in difficulties[:4]:
                lines.append(f"- {diff}")

        lines.extend([
            "",
            "## 🔍 Pesquisa Preparatoria",
            "",
            f"- **YouTube:** pesquise \"{module.front.value} {module.cefr_level.value} tutorial\"",
            f"- **BBC Learning English:** procure pela serie '{module.cefr_level.value} drama' ou '6 Minute Grammar'",
            f"- **Cambridge Dictionary:** busque exemplos de uso em contexto (dictionary.cambridge.org)",
            "",
            "## 💡 Dicas de Estudo",
            "",
            "- Tente **ler em voz alta** todo o material — isso ativa memoria muscular",
            "- **Pratique 15 minutos por dia** em vez de 2 horas uma vez por semana",
            "- Grave sua voz e compare com nativos (apps: ELSA Speak, Speechling)",
            "- Crie **flashcards** com Anki para vocabulario novo",
            "",
            "## 🎬 Consumo Recomendado",
            "",
            self._recommended_content(module.cefr_level, module.front, module.title),
            "",
            "---",
            "",
            f"_Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}_",
        ])
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    def _get_next_module(self, state: LearnerState, current: Module) -> Optional[Module]:
        """Return the next pending module after the current one."""
        found = False
        for m in state.modules:
            if m.id == current.id:
                found = True
                continue
            if found and m.status == "pending":
                return m
        return None

    def _next_level(self, state: LearnerState) -> Optional[CefrLevel]:
        avg = sum(state.front_scores.values()) / len(state.front_scores) if state.front_scores else 0
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
        return None

    def _slugify(self, text: str) -> str:
        """Convert 'Introductions & Greetings' -> 'introductions-and-greetings'."""
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9\s-]", "", text)
        text = re.sub(r"\s+", "-", text)
        return text[:48]

    def _ptbr_tips(self, front: Front) -> str:
        """Return PT-BR specific tips per front."""
        tips = {
            Front.GRAMMAR: (
                "- **Nao existe present perfect em PT-BR** → pratique com 'have you ever...?'\n"
                "- **Falta de auxiliares** → lembre: perguntas precisam de do/does/did\n"
                "- **3a pessoa -s** → he/she/it **does** (nao 'he do')\n"
                "- **Preposicoes** → depend **ON** (nao 'depend of'), married **TO** (nao 'married with')"
            ),
            Front.VOCABULARY: (
                "- **Falsos cognatos:** actually (na verdade) ≠ atualmente, pretend (fingir) ≠ pretender\n"
                "- **Library** (biblioteca) ≠ livraria (bookstore)\n"
                "- **Parents** (pais) ≠ parentes (relatives)\n"
                "- **Push** (empurrar) ≠ puxar (pull)"
            ),
            Front.PRONUNCIATION: (
                "- **/θ/ e /ð/** (th): poe a lingua entre os dentes — 'think', 'the'\n"
                "- **/h/ aspirado**: tem som de 'r' suave — 'house', 'hello'\n"
                "- **Schwa /ə/**: o som mais comum do ingles — 'a'bout, 'e'lephant\n"
                "- **Can vs Can't**: can't tem vogal mais longa e parada glotal no final"
            ),
            Front.WRITING: (
                "- **Estruture em paragrafos:** idea principal → suporte → conclusao\n"
                "- **Evite traduzir literalmente** do portugues\n"
                "- **Use conectivos:** however, therefore, moreover, in addition\n"
                "- **Pratique com journaling:** 5 frases por dia sobre seu dia"
            ),
            Front.LISTENING: (
                "- **Nao tente entender cada palavra** → foque no sentido geral\n"
                "- **Assista com legendas em INGLES** (nao em PT-BR)\n"
                "- **BBC 6 Minute English** → otimo para listening A2-B1\n"
                "- **Pause e repita** frases curtas em voz alta"
            ),
            Front.SPEAKING: (
                "- **Fale sozinho(a)!** Narre o que esta fazendo em casa\n"
                "- **Pense em ingles** — nao traduza do portugues\n"
                "- **Grave audio** e compare com nativos\n"
                "- **Errar e necessario** — errar faz parte do processo"
            ),
        }
        return tips.get(front, "- Pratique regularmente e nao tenha medo de errar!")

    def _recommended_content(self, level: CefrLevel, front: Front, title: str) -> str:
        """Return recommended content to consume per level and front."""
        base = {
            "youtube": {
                "A1": "English with Lucy (basics), BBC Learning English (beginners)",
                "A2": "English with Lucy, BBC 6 Minute English, Learn English with TV Series",
                "B1": "BBC 6 Minute English, TED-Ed, English with Cambridge",
                "B2": "TED Talks, BBC News, Vox, The Economist (video)",
                "C1": "The Economist, Channel 4 News, PBS, NPR",
                "C2": "BBC World Service, The Guardian (audio), C-SPAN, academic lectures",
            },
            "podcasts": {
                "A1": "Voice of America (Learning English), ESL Pod",
                "A2": "6 Minute English (BBC), All Ears English",
                "B1": "6 Minute English, All Ears English, The English We Speak",
                "B2": "The Daily (NYT), Radiolab, Stuff You Should Know",
                "C1": "The Daily, Radiolab, Fresh Air, Hidden Brain",
                "C2": "The Economist (audio), BBC In Our Time, Philosophy Bites",
            },
            "sites": {
                "A1": "British Council (Learn English), Cambridge English (kids)",
                "A2": "British Council (Learn English), Perfect English Grammar",
                "B1": "British Council, BBC Learning English, Grammarly Blog",
                "B2": "BBC News (Easy Read), The Guardian, Grammarly Blog",
                "C1": "The Guardian, The Atlantic, BBC Future",
                "C2": "The Atlantic, New Yorker, The Economist, academic journals",
            },
        }

        lv = level.value
        yt = base["youtube"].get(lv, "YouTube English learning channels")
        pod = base["podcasts"].get(lv, "English learning podcasts")
        sites = base["sites"].get(lv, "English learning websites")

        return (
            f"- **YouTube:** {yt}\n"
            f"- **Podcasts:** {pod}\n"
            f"- **Sites:** {sites}\n"
            f"- **Pronuncia:** YouGlish (youglish.com), Forvo (forvo.com), ELSA Speak"
        )
