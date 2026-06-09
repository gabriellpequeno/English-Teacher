# Memory System — Instruções para Agentes de Desenvolvimento

> Exclusivo para agents **construindo features do projeto**.
> **NUNCA** usado durante o Modo Estudo (ensino de inglês).

## Regras

1. **Antes de cada task**, leia todos os `.md` em `.memory/`
2. Aplique **automaticamente** padrões com `Status: confirmed`
3. Padrões `Status: suggested` exigem **confirmação do usuário**
4. Se notar um padrão novo (3+ ocorrências consistentes), **pergunte** ao usuário se quer registrar
5. **NUNCA** use `.memory/` durante interações do Modo Estudo

## Fluxo

```
ANTES DA TASK:
  1. glob .memory/*.md
  2. read cada arquivo
  3. Extraia padroes confirmed e aplique

DURANTE A TASK:
  4. Siga os padroes aprendidos

DEPOIS DA TASK:
  5. Detectou padrao novo? Pergunte ao usuario
  6. Se confirmado, adicione ao .memory/patterns.md
```

## Formato ao adicionar um padrão

```markdown
## id-001: Titulo do padrao
- **Status**: suggested
- **Confidence**: medium
- **Category**: workflow | code | decision | technical
- **Learned**: YYYY-MM-DD
- **Source**: Identificado durante implementação de X

Descrição clara do padrão.

### Evidence
- Exemplo concreto 1
- Exemplo concreto 2
```

## Isolamento

**Study agents** (estudo, classifier, builder, teacher, tester, tracker, coach, material, tuto)
NÃO devem acessar `.memory/`. Eles só veem `src/knowledge/` e `src/agents/`.

Se estiver no Modo Estudo, ignore completamente o `.memory/`.
