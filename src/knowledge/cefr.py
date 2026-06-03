"""
Common European Framework of Reference for Languages (CEFR)
Descritores baseados no Council of Europe (2001, 2020)
Referência oficial: https://www.coe.int/en/web/common-european-framework-reference-languages
"""

from typing import Dict, List
from src.state import CefrLevel, Front


CEFR_DESCRIPTORS: Dict[CefrLevel, Dict[str, List[str]]] = {
    CefrLevel.A1: {
        "writing": [
            "Consegue escrever um postal curto e simples",
            "Preenche formulários com dados pessoais",
            "Escreve frases isoladas sobre si mesmo"
        ],
        "listening": [
            "Reconhece palavras familiares e expressões básicas",
            "Compreende fala lenta e clara com pausas",
            "Entende números, preços, horas"
        ],
        "speaking": [
            "Apresenta-se e usa saudações básicas",
            "Fala frases memorizadas sobre si mesmo",
            "Responde perguntas simples e diretas"
        ],
        "grammar": [
            "Verbo to be no presente",
            "Present simple (like, live, work)",
            "Artigos indefinidos (a/an)",
            "Pronomes pessoais e possessivos"
        ],
        "vocabulary": [
            "Números, cores, dias da semana",
            "Família, casa, objetos cotidianos",
            "Comida e bebida básica"
        ],
        "pronunciation": [
            "Sons básicos do alfabeto",
            "Distinção entre vogais curtas e longas"
        ]
    },
    CefrLevel.A2: {
        "writing": [
            "Escreve notas e mensagens curtas",
            "Descreve família, condições de vida, formação",
            "Escreve sobre atividades diárias"
        ],
        "listening": [
            "Compreende frases e expressões de uso frequente",
            "Entende o essencial de anúncios curtos",
            "Acompanha fala clara sobre temas familiares"
        ],
        "speaking": [
            "Comunica em tarefas simples e rotineiras",
            "Descreve pessoas, lugares, posses",
            "Faz pedidos e responde a ofertas"
        ],
        "grammar": [
            "Present continuous",
            "Past simple (was/were, regular/irregular)",
            "There is/are",
            "Preposições de tempo (in, on, at)"
        ],
        "vocabulary": [
            "Rotina diária, trabalho, escola",
            "Clima, estações do ano",
            "Direções e lugares na cidade"
        ],
        "pronunciation": [
            "Contrações (I'm, don't, can't)",
            "Entonação em perguntas"
        ]
    },
    CefrLevel.B1: {
        "writing": [
            "Escreve textos coerentes sobre temas familiares",
            "Descreve experiências, eventos, sonhos",
            "Escreve cartas pessoais com opiniões"
        ],
        "listening": [
            "Compreende fala clara sobre trabalho/escola/lazer",
            "Entende programas de rádio/TV com ritmo normal",
            "Capta ideias principais de palestras curtas"
        ],
        "speaking": [
            "Lida com a maioria das situações de viagem",
            "Participa de conversas sobre temas familiares",
            "Expressa opiniões, planos, sentimentos"
        ],
        "grammar": [
            "Present perfect (experiências)",
            "Futuro com will e going to",
            "First conditional",
            "Voz passiva (present simple)"
        ],
        "vocabulary": [
            "Viagem, turismo, transporte",
            "Saúde, corpo, sintomas",
            "Tecnologia e internet"
        ],
        "pronunciation": [
            "Connected speech (linking)",
            "Weak forms (schwa)",
            "Stress em palavras de 2+ sílabas"
        ]
    },
    CefrLevel.B2: {
        "writing": [
            "Escreve textos detalhados sobre diversos temas",
            "Desenvolve argumentos com prós e contras",
            "Escreve redações, relatórios, cartas formais"
        ],
        "listening": [
            "Compreende discursos longos e complexos",
            "Acompanha filmes sem legendas com esforço",
            "Entende noticiários e documentários"
        ],
        "speaking": [
            "Conversa com fluência natural sem esforço",
            "Defende opiniões em discussões",
            "Fala sobre temas abstratos"
        ],
        "grammar": [
            "Second e third conditional",
            "Voz passiva em todos os tempos",
            "Relative clauses (defining/non-defining)",
            "Reported speech"
        ],
        "vocabulary": [
            "Negócios, economia, política básica",
            "Meio ambiente e sociedade",
            "Expressões idiomáticas comuns"
        ],
        "pronunciation": [
            "Intonation for attitude and emotion",
            "Sentence stress for emphasis",
            "Distinção entre fonemas similares"
        ]
    },
    CefrLevel.C1: {
        "writing": [
            "Escreve textos complexos, claros e bem estruturados",
            "Adapta estilo ao leitor alvo",
            "Produz textos acadêmicos e profissionais"
        ],
        "listening": [
            "Compreende fala rápida e implícita",
            "Entende filmes e TV sem esforço",
            "Acompanha discussões entre falantes nativos"
        ],
        "speaking": [
            "Expressa-se fluentemente sem hesitação",
            "Usa linguagem flexível para diferentes contextos",
            "Produz discurso claro e bem organizado"
        ],
        "grammar": [
            "Inversion (never have I...), cleft sentences",
            "Mixed conditionals",
            "Modais no passado (must have, should have)",
            "Advanced passive constructions"
        ],
        "vocabulary": [
            "Academic and formal vocabulary",
            "Collocations e phrasal verbs avançados",
            "Nuances e sinônimos precisos"
        ],
        "pronunciation": [
            "Natural rhythm and intonation patterns",
            "Regional accent variation awareness",
            "Emphasis for rhetorical effect"
        ]
    },
    CefrLevel.C2: {
        "writing": [
            "Escreve com precisão e estilo apropriado",
            "Produz textos acadêmicos publicáveis",
            "Domina gêneros textuais complexos"
        ],
        "listening": [
            "Compreende qualquer tipo de fala sem esforço",
            "Entende sotaques e dialetos variados",
            "Capta humor, ironia e sutilezas"
        ],
        "speaking": [
            "Comunica-se com precisão e naturalidade total",
            "Negocia significados complexos",
            "Equivalente a falante nativo educado"
        ],
        "grammar": [
            "Domínio completo e consistente",
            "Uso sofisticado de estruturas",
            "Gramática implícita e intuitiva"
        ],
        "vocabulary": [
            "Domínio lexical extenso e preciso",
            "Expressões idiomáticas e coloquiais",
            "Registros formal e informal"
        ],
        "pronunciation": [
            "Prosódia natural em todos os contextos",
            "Controle de ênfase e tom para significado fino"
        ]
    }
}

CEFR_GLOBAL_SCALE: Dict[CefrLevel, str] = {
    CefrLevel.A1: "Básico: consegue compreender e usar expressões familiares e quotidianas.",
    CefrLevel.A2: "Elementar: consegue comunicar em tarefas simples e rotineiras.",
    CefrLevel.B1: "Independente: consegue lidar com a maioria das situações de viagem.",
    CefrLevel.B2: "Independente avançado: consegue interagir com fluência natural.",
    CefrLevel.C1: "Proficiente: consegue expressar-se fluentemente sobre temas complexos.",
    CefrLevel.C2: "Mestre: compreende praticamente tudo que ouve ou lê.",
}

CEFR_OFFICIAL_RESOURCES = {
    "framework": "https://www.coe.int/en/web/common-european-framework-reference-languages",
    "self_assessment": "https://rm.coe.int/CoERMPublicCommonSearchServices/DisplayDCTMContent?documentId=090000168045bb52",
    "cambridge_align": "https://www.cambridgeenglish.org/exams-and-tests/cefr/",
    "ef_set": "https://www.efset.org/cefr/",
    "british_council": "https://learnenglish.britishcouncil.org/english-levels",
}


def get_descriptors(level: CefrLevel, front: Front) -> List[str]:
    return CEFR_DESCRIPTORS.get(level, {}).get(front.value, [])


def get_all_descriptors(level: CefrLevel) -> Dict[str, List[str]]:
    return CEFR_DESCRIPTORS.get(level, {})


def estimate_level_from_scores(front_scores: Dict[Front, float]) -> CefrLevel:
    avg = sum(front_scores.values()) / len(front_scores)
    if avg >= 95: return CefrLevel.C2
    if avg >= 80: return CefrLevel.C1
    if avg >= 60: return CefrLevel.B2
    if avg >= 40: return CefrLevel.B1
    if avg >= 20: return CefrLevel.A2
    return CefrLevel.A1


def level_progression(from_level: CefrLevel, to_level: CefrLevel) -> List[CefrLevel]:
    order = [CefrLevel.A1, CefrLevel.A2, CefrLevel.B1, CefrLevel.B2, CefrLevel.C1, CefrLevel.C2]
    start = order.index(from_level)
    end = order.index(to_level)
    return order[start:end + 1]
