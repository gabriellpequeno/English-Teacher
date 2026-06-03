"""
Ferramenta de busca na web para os agentes.
Usa fontes oficiais e abertas de aprendizado de inglês.

Fontes configuradas:
- British Council: https://learnenglish.britishcouncil.org/
- BBC Learning English: https://www.bbc.co.uk/learningenglish/
- Cambridge English: https://www.cambridgeenglish.org/
- YouGlish: https://youglish.com/ (pronúncia)
- Forvo: https://forvo.com/ (pronúncia)
- EF SET: https://www.efset.org/ (teste de nível)
"""

import json
import urllib.request
import urllib.parse
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str


OFFICIAL_RESOURCES = {
    "british_council": {
        "name": "British Council Learn English",
        "url": "https://learnenglish.britishcouncil.org/",
        "levels": "https://learnenglish.britishcouncil.org/english-levels",
        "grammar": "https://learnenglish.britishcouncil.org/grammar",
        "skills": "https://learnenglish.britishcouncil.org/skills",
    },
    "bbc_learning": {
        "name": "BBC Learning English",
        "url": "https://www.bbc.co.uk/learningenglish/",
        "pronunciation": "https://www.bbc.co.uk/learningenglish/features/pronunciation",
    },
    "cambridge": {
        "name": "Cambridge English",
        "url": "https://www.cambridgeenglish.org/",
        "cefr": "https://www.cambridgeenglish.org/exams-and-tests/cefr/",
        "exams": "https://www.cambridgeenglish.org/exams-and-tests/",
    },
    "youglish": {
        "name": "YouGlish",
        "url": "https://youglish.com/",
        "description": "Busca pronúncia em vídeos do YouTube",
    },
    "forvo": {
        "name": "Forvo",
        "url": "https://forvo.com/",
        "description": "Dicionário de pronúncia com falantes nativos",
    },
    "ef_set": {
        "name": "EF Standard English Test",
        "url": "https://www.efset.org/",
        "description": "Teste de nível gratuito alinhado ao CEFR",
    },
    "merriam_webster": {
        "name": "Merriam-Webster Dictionary",
        "url": "https://www.merriam-webster.com/",
        "description": "Dicionário com pronúncia em áudio",
    },
}


class WebSearchTool:
    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        if not self.enabled:
            return self._local_search(query, max_results)
        try:
            return self._web_search(query, max_results)
        except Exception:
            return self._local_search(query, max_results)

    def _web_search(self, query: str, max_results: int) -> List[SearchResult]:
        encoded = urllib.parse.quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1"
        req = urllib.request.Request(url, headers={"User-Agent": "EnglishTeacher/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        results = []
        for topic in data.get("RelatedTopics", [])[:max_results]:
            if "Text" in topic and "FirstURL" in topic:
                results.append(SearchResult(
                    title=topic.get("Text", "").split(" - ")[0],
                    url=topic.get("FirstURL", ""),
                    snippet=topic.get("Text", ""),
                    source="web"
                ))
        return results

    def _local_search(self, query: str, max_results: int) -> List[SearchResult]:
        query_lower = query.lower()
        results = []
        for key, resource in OFFICIAL_RESOURCES.items():
            score = 0
            for val in resource.values():
                if isinstance(val, str) and query_lower in val.lower():
                    score += 2
            if query_lower in key.replace("_", " "):
                score += 3
            if score > 0:
                results.append(SearchResult(
                    title=resource.get("name", key),
                    url=resource.get("url", ""),
                    snippet=self._get_resource_snippet(key, query),
                    source=key
                ))
        for d in results[:max_results]:
            pass
        return results[:max_results]

    def _get_resource_snippet(self, key: str, query: str) -> str:
        snippets = {
            "british_council": "Cursos gratuitos de inglês por nível (A1-C2) com exercícios de gramática, listening, reading e writing.",
            "bbc_learning": "Aulas de inglês da BBC com foco em pronúncia, vocabulário e compreensão auditiva.",
            "cambridge": "Material oficial de preparação para exames Cambridge alinhado ao CEFR.",
            "youglish": "Busca por palavras em vídeos do YouTube para ouvir pronúncia em contexto real.",
            "forvo": "Dicionário de pronúncia com gravações de falantes nativos do mundo todo.",
            "ef_set": "Teste de nivelamento de inglês gratuito de 50 minutos com certificado alinhado ao CEFR.",
            "merriam_webster": "Dicionário americano com pronúncia em áudio, exemplos e origem das palavras.",
        }
        return snippets.get(key, f"Recurso educacional para inglês: {key}")

    def get_resource_url(self, resource: str, path: str = "") -> str:
        if resource in OFFICIAL_RESOURCES:
            base = OFFICIAL_RESOURCES[resource]["url"]
            return base + path
        return ""


class KnowledgeBaseTool:
    def __init__(self):
        from src.knowledge.cefr import CEFR_DESCRIPTORS, CEFR_GLOBAL_SCALE, CEFR_OFFICIAL_RESOURCES
        from src.knowledge.ptbr_phonetics import (
            PTBR_PHONETIC_DIFFICULTIES, GRAMMAR_DIFFICULTIES,
            get_difficulties_by_level
        )
        self.cefr_descriptors = CEFR_DESCRIPTORS
        self.cefr_global = CEFR_GLOBAL_SCALE
        self.cefr_resources = CEFR_OFFICIAL_RESOURCES
        self.phonetics = PTBR_PHONETIC_DIFFICULTIES
        self.grammar = GRAMMAR_DIFFICULTIES
        self.get_ptbr_difficulties = get_difficulties_by_level

    def query_cefr(self, level: Optional[str] = None) -> str:
        from state import CefrLevel
        if level:
            try:
                lvl = CefrLevel(level.upper())
                desc = self.cefr_descriptors.get(lvl, {})
                global_desc = self.cefr_global.get(lvl, "")
                lines = [f"--- CEFR {lvl.value}: {global_desc} ---"]
                for front, items in desc.items():
                    lines.append(f"\n{front.upper()}:")
                    for item in items:
                        lines.append(f"  - {item}")
                return "\n".join(lines)
            except ValueError:
                return f"Nível CEFR inválido: {level}"
        lines = ["--- CEFR Global Scale ---"]
        for lvl, desc in self.cefr_global.items():
            lines.append(f"  {lvl.value}: {desc}")
        return "\n".join(lines)

    def query_phonetics(self, issue_id: Optional[str] = None) -> str:
        items = self.phonetics
        if issue_id:
            items = [d for d in items if d["id"] == issue_id]
        if not items:
            return "Nenhuma dificuldade fonética encontrada."
        lines = ["--- Dificuldades Fonéticas PT-BR → EN ---"]
        for d in items:
            lines.append(f"\n• {d.get('sound', '')} - {d['description']}")
            lines.append(f"  Substituição comum: {d.get('pt_br_substitution', 'N/A')}")
            if d.get("examples"):
                lines.append(f"  Exemplos: {', '.join(d['examples'][:3])}")
            if d.get("minimal_pairs"):
                pairs = [f"{a}/{b}" for a, b in d["minimal_pairs"][:3]]
                lines.append(f"  Minimal pairs: {', '.join(pairs)}")
        return "\n".join(lines)

    def query_grammar(self) -> str:
        lines = ["--- Dificuldades Gramaticais PT-BR → EN ---"]
        for d in self.grammar:
            lines.append(f"\n• {d['description']}")
            if d.get("examples"):
                for ex in d["examples"][:3]:
                    lines.append(f"  → {ex}")
        return "\n".join(lines)
