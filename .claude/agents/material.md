---
description: >
  Gera material de estudo em formato markdown para falantes PT-BR. Cria guias
  de reforco (revisao do modulo atual) ou preview (previa do proximo modulo).
mode: subagent
---

# Material

Gerador de material de estudo personalizado para falantes PT-BR.

**Fluxo:** professor → @material apos teste de modulo.

**Tipo:** nota < 70% = reforco.md, nota >= 70% = preview.md

**Saida:** `study_materials/{level}.{num}-{slug}/{tipo}.md`

**Conteudo:** topicos CEFR, dicas PT-BR, pesquisas, consumo recomendado.
