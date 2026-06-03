"""
Dificuldades foneticas especificas de falantes nativos de portugues brasileiro (PT-BR)
ao aprender ingles. Baseado em estudos de Linguistica Contrastiva e Analise de Erros.

Fontes:
- Swan & Smith (2001) "Learner English" - Capitulo sobre portugues
- Baptista & Watkins (2006) "English with a Latin Beat"
- Zimmer, Silveira & Alves (2016) "Pronunciation Instruction for Brazilians"
"""

from typing import Dict, List, Tuple


PhoneticIssue = Dict[str, object]

PTBR_PHONETIC_DIFFICULTIES: List[PhoneticIssue] = [
    {
        "id": "th_voiceless",
        "sound": "/theta/",
        "description": "Som 'th' surdo (think, thanks, three)",
        "pt_br_substitution": "/f/ ou /t/",
        "examples": ["think -> fink/tink", "three -> free/tree", "thanks -> tanks/fanks"],
        "minimal_pairs": [("think", "sink"), ("thin", "tin"), ("thick", "tick")],
        "difficulty": "high",
        "cefr_start": "A1",
    },
    {
        "id": "th_voiced",
        "sound": "/eth/",
        "description": "Som 'th' sonoro (the, this, mother, with)",
        "pt_br_substitution": "/d/ ou /z/",
        "examples": ["the -> duh/ze", "mother -> moder", "with -> wid/wiz"],
        "minimal_pairs": [("they", "day"), ("then", "den"), ("breathe", "breed")],
        "difficulty": "high",
        "cefr_start": "A1",
    },
    {
        "id": "h_sound",
        "sound": "/h/",
        "description": "Som 'h' aspirado (house, happy, who)",
        "pt_br_substitution": "omissao (portugues nao tem /h/)",
        "examples": ["house -> 'ouse", "happy -> 'appy", "who -> 'oo"],
        "minimal_pairs": [("heat", "eat"), ("hill", "ill"), ("hair", "air")],
        "difficulty": "medium",
        "cefr_start": "A1",
    },
    {
        "id": "schwa",
        "sound": "/schwa/",
        "description": "Schwa - vogal neutra (about, banana, the)",
        "pt_br_substitution": "vogal plena, geralmente /a/ ou /e/",
        "examples": ["about -> a-bout (sem schwa)", "banana -> ba-na-na"],
        "minimal_pairs": [],
        "difficulty": "high",
        "cefr_start": "A2",
    },
    {
        "id": "vowel_length",
        "sound": "short vs long vowels",
        "description": "Distincao entre vogais curtas e longas",
        "pt_br_substitution": "portugues nao distingue por duracao",
        "examples": ["ship vs sheep", "full vs fool", "hit vs heat"],
        "minimal_pairs": [
            ("ship", "sheep"), ("live", "leave"),
            ("full", "fool"), ("hit", "heat"), ("cot", "caught"),
        ],
        "difficulty": "high",
        "cefr_start": "A1",
    },
    {
        "id": "final_consonants",
        "sound": "consoantes finais",
        "description": "Consoantes em posicao final de silaba (portugues tende a abrir silabas)",
        "pt_br_substitution": "adicao de /i/ ou /e/ epentetico",
        "examples": ["dog -> dogi/doge", "big -> bigi", "stop -> stopi"],
        "minimal_pairs": [],
        "difficulty": "medium",
        "cefr_start": "A1",
    },
    {
        "id": "r_sounds",
        "sound": "/r/",
        "description": "Som 'r' em inicio de silaba (red, write, around)",
        "pt_br_substitution": "/h/ aspirado ou /x/",
        "examples": ["red -> hred/xed", "write -> hrite"],
        "minimal_pairs": [],
        "difficulty": "medium",
        "cefr_start": "A2",
    },
    {
        "id": "l_dark",
        "sound": "/l/ escuro (dark L)",
        "description": "'L' no final de silaba (milk, ball, help)",
        "pt_br_substitution": "/w/ (como no portugues: 'mal' -> 'maw')",
        "examples": ["milk -> miwk", "ball -> baw", "help -> hewp"],
        "minimal_pairs": [],
        "difficulty": "medium",
        "cefr_start": "A2",
    },
    {
        "id": "word_stress",
        "sound": "acentuacao lexical",
        "description": "Padrao de stress imprevisivel em ingles",
        "pt_br_substitution": "tendencia a acentuar na segunda silaba (padrao PT-BR)",
        "examples": ["PHOtograph -> phoTOgraph", "REcord (n) vs reCORD (v)"],
        "minimal_pairs": [
            ("REcord (noun)", "reCORD (verb)"),
            ("PREsent (noun)", "preSENT (verb)"),
            ("CONduct (noun)", "conDUCT (verb)"),
        ],
        "difficulty": "high",
        "cefr_start": "B1",
    },
    {
        "id": "s_plural_pronunciation",
        "sound": "/s/, /z/, /iz/",
        "description": "Pronuncia do plural/terceira pessoa (-s)",
        "pt_br_substitution": "sempre /s/",
        "examples": ["dogs -> dogz (correto), cats -> cat-s (correto)"],
        "minimal_pairs": [],
        "difficulty": "medium",
        "cefr_start": "A2",
    },
    {
        "id": "ed_ending",
        "sound": "/t/, /d/, /id/",
        "description": "Pronuncia do -ed (passado)",
        "pt_br_substitution": "sempre /d/ ou /ed/",
        "examples": ["walked -> walkt (correto), wanted -> wantid (correto)"],
        "minimal_pairs": [],
        "difficulty": "medium",
        "cefr_start": "A2",
    },
    {
        "id": "can_cant_distinction",
        "sound": "can vs can't",
        "description": "Diferenca entre can (fraca) e can't (forte/longa)",
        "pt_br_substitution": "tendencia a nao distinguir",
        "examples": ["I can swim (schwa) vs I can't swim (vogal longa/t final)"],
        "minimal_pairs": [("can", "can't")],
        "difficulty": "high",
        "cefr_start": "B1",
    },
]

GRAMMAR_DIFFICULTIES: List[PhoneticIssue] = [
    {
        "id": "no_verb_inflection_pt",
        "description": "Portugues tem flexao verbal rica; ingles tem pouca flexao",
        "examples": [
            "He go (ao inves de goes) - omitindo -s da 3a pessoa",
            "She don't (ao inves de doesn't)",
        ],
        "difficulty": "medium",
        "cefr_start": "A1",
    },
    {
        "id": "auxiliary_questions",
        "description": "Formacao de perguntas com auxiliares (do/does/did)",
        "examples": [
            "You like pizza? (ao inves de Do you like pizza?)",
            "Why you did that? (ao inves de Why did you do that?)",
        ],
        "difficulty": "high",
        "cefr_start": "A1",
    },
    {
        "id": "prepositions",
        "description": "Preposicoes diferentes entre PT-BR e EN",
        "examples": [
            "I'm in the bus (ao inves de on the bus)",
            "Depend of (ao inves de depend on)",
            "She's married with (ao inves de married to)",
        ],
        "difficulty": "high",
        "cefr_start": "A2",
    },
    {
        "id": "false_cognates",
        "description": "Falsos cognatos (false friends)",
        "examples": [
            "actually (na verdade) != atualmente (currently)",
            "pretend (fingir) != pretender (intend)",
            "library (biblioteca) != livraria (bookstore)",
            "push (empurrar) != puxar (pull)",
            "parents (pais) != parentes (relatives)",
        ],
        "difficulty": "high",
        "cefr_start": "A2",
    },
    {
        "id": "present_perfect",
        "description": "Present Perfect ('I have seen') nao existe em PT-BR",
        "examples": [
            "I already saw (ao inves de I've already seen)",
            "She didn't arrive yet (ao inves de She hasn't arrived yet)",
        ],
        "difficulty": "high",
        "cefr_start": "B1",
    },
    {
        "id": "conditional",
        "description": "Estruturas condicionais (diferentes do portugues)",
        "examples": [
            "If I would go (ao inves de If I went - second conditional)",
            "If I have money, I would buy (mistura de first e second)",
        ],
        "difficulty": "high",
        "cefr_start": "B1",
    },
]

CULTURAL_NOTES = [
    "Falantes de PT-BR tendem a ser mais diretos em pedidos (imperativo) - em ingles eh mais educado usar 'Could you...'",
    "Uso excessivo de 'please' no inicio vs final da frase",
    "Tamanho do turno: brasileiros costumam falar mais tempo em conversas",
    "Feedback em conversa: brasileiros usam mais 'sim' (yes) como backchannel",
]


def get_difficulties_by_level(cefr_level: str) -> List[PhoneticIssue]:
    result = []
    for d in PTBR_PHONETIC_DIFFICULTIES + GRAMMAR_DIFFICULTIES:
        if d.get("cefr_start", "A1") <= cefr_level:
            result.append(d)
    return result


def get_phonetic_difficulties() -> List[PhoneticIssue]:
    return PTBR_PHONETIC_DIFFICULTIES


def get_grammar_difficulties() -> List[PhoneticIssue]:
    return GRAMMAR_DIFFICULTIES


def get_minimal_pairs_for_issue(issue_id: str) -> List[Tuple[str, str]]:
    for d in PTBR_PHONETIC_DIFFICULTIES:
        if d["id"] == issue_id:
            return d.get("minimal_pairs", [])
    return []
