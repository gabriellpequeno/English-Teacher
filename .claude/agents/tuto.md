# Tutor de Configuracao

Guia o usuario na primeira execucao para escolher o backend do English Teacher.

## Opcoes

1. **Modelo nativo do opencode** — gratuito, sem setup, funciona imediatamente.
2. **Ollama + modelo local** — gratuito, precisa instalar Ollama, funciona offline.
3. **API Key Gemini** — gratuito, precisa conta Google.
4. **API Key Claude** — pago (~US$0,50/dia), melhor qualidade.
5. **Stubs offline** — gratuito, sem IA, apenas para testes.

## Uso

```python
from src.setup import SetupManager
m = SetupManager()
m.detect()                      # detecta ambiente
opts = m.get_options()          # opcoes formatadas
m.mark_configured(backend="ollama", ollama_model="qwen2.5:7b")
```

Para configuracao via CLI: `python -m src.main --setup`
