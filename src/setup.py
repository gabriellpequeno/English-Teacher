from __future__ import annotations
import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

SETUP_PATH = Path(__file__).parent / "knowledge" / "setup.json"

DEFAULT_SETUP: Dict[str, Any] = {
    "configured": False,
    "configured_at": None,
    "backend": None,
    "ollama_model": "qwen2.5:7b",
    "ollama_available": False,
    "ollama_installed": None,
    "api_key_providers": [],
    "context": None,
    "last_detected": None,
    "tuto_completed_steps": [],
}

OLLAMA_DOWNLOAD = "https://ollama.com/download"
OLLAMA_DOCS = "https://github.com/ollama/ollama"
ANTHROPIC_SIGNUP = "https://console.anthropic.com/"
OPENAI_SIGNUP = "https://platform.openai.com/api-keys"
GEMINI_SIGNUP = "https://aistudio.google.com/apikey"
OPENROUTER_SIGNUP = "https://openrouter.ai/keys"


class SetupManager:
    def __init__(self, context: Optional[str] = None):
        self.data = self._load()
        if context:
            self.data["context"] = context

    def _load(self) -> Dict[str, Any]:
        if SETUP_PATH.exists():
            with open(SETUP_PATH, encoding="utf-8") as f:
                stored = json.load(f)
            merged = dict(DEFAULT_SETUP)
            merged.update(stored)
            return merged
        return dict(DEFAULT_SETUP)

    def _save(self) -> None:
        SETUP_PATH.parent.mkdir(exist_ok=True)
        with open(SETUP_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def detect(self) -> Dict[str, Any]:
        self.data["context"] = self.data.get("context") or self._detect_context()
        self.data["ollama_available"] = self._check_ollama_api()
        self.data["ollama_installed"] = self._check_ollama_binary()
        self.data["api_key_providers"] = self._detect_api_keys()
        self.data["last_detected"] = datetime.now().isoformat()
        self._save()
        return self.data

    def _detect_context(self) -> str:
        if "OPENCODE_AGENT" in os.environ:
            return "opencode"
        if "CLAUDE_CODE" in os.environ:
            return "claude"
        if Path(".opencode").is_dir():
            return "opencode"
        if "--opencode" in " ".join(sys.argv).lower():
            return "opencode"
        return "python"

    def _check_ollama_api(self) -> bool:
        try:
            req = urllib.request.Request(
                "http://localhost:11434/api/tags",
                method="GET",
                headers={"User-Agent": "EnglishTeacher/1.0"},
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _check_ollama_binary(self) -> Optional[str]:
        paths = [
            r"C:\Program Files\Ollama\ollama.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Ollama\ollama.exe"),
            "/usr/local/bin/ollama",
            "/usr/bin/ollama",
            os.path.expanduser("~/.ollama/bin/ollama"),
        ]
        for p in paths:
            if os.path.exists(p):
                return p
        return None

    def _detect_api_keys(self) -> List[Dict[str, str]]:
        checks = [
            ("anthropic", "ANTHROPIC_API_KEY", "Claude (Anthropic)", True),
            ("openai", "OPENAI_API_KEY", "OpenAI (GPT-4, etc.)", True),
            ("google", "GOOGLE_API_KEY", "Google AI (Gemini)", False),
            ("gemini", "GEMINI_API_KEY", "Gemini API (alternativo)", False),
            ("openrouter", "OPENROUTER_API_KEY", "OpenRouter", False),
        ]
        found = []
        for pid, env, label, paid in checks:
            val = os.environ.get(env)
            if val and val.strip() and len(val.strip()) > 5:
                found.append({"id": pid, "env_var": env, "label": label, "paid": paid})
        return found

    def is_first_run(self) -> bool:
        return not self.data.get("configured", False)

    def mark_configured(self, backend: str, **kwargs) -> None:
        self.data["configured"] = True
        self.data["configured_at"] = datetime.now().isoformat()
        self.data["backend"] = backend
        for k, v in kwargs.items():
            self.data[k] = v
        self._save()

    def get_options(self) -> List[Dict[str, Any]]:
        context = self.data.get("context", "python")
        ollama_api = self.data.get("ollama_available", False)
        ollama_bin = self.data.get("ollama_installed")
        keys = self.data.get("api_key_providers", [])
        opts = []
        n = 0

        if context in ("opencode",):
            n += 1
            opts.append({
                "id": "native", "num": n,
                "title": "Modelo nativo do opencode",
                "cost": "gratuito", "setup": "Nenhum — já funciona!",
                "quality": "Boa",
                "note": "Usa o modelo padrão do opencode CLI. Todos os agentes usam o mesmo modelo. Sem instalação ou chave.",
                "status": "disponivel", "guide_urls": [],
            })

        if ollama_api:
            n += 1
            opts.append({
                "id": "ollama", "num": n,
                "title": "Ollama (já rodando!)",
                "cost": "gratuito", "setup": "Só escolher o modelo",
                "quality": "Muito boa",
                "note": "Ollama detectado e rodando. Basta configurar qual modelo usar. Funciona offline, sem chave.",
                "status": "rodando", "guide_urls": [OLLAMA_DOCS],
            })
        elif ollama_bin:
            n += 1
            opts.append({
                "id": "ollama", "num": n,
                "title": "Ollama (instalado, não rodando)",
                "cost": "gratuito", "setup": "Iniciar servidor",
                "quality": "Muito boa",
                "note": f"Instalado em {ollama_bin}. Execute 'ollama serve' para iniciar.",
                "status": "parado", "guide_urls": [OLLAMA_DOCS],
            })
        else:
            n += 1
            opts.append({
                "id": "ollama", "num": n,
                "title": "Ollama + modelo local",
                "cost": "gratuito", "setup": "Precisa instalar (~5 min)",
                "quality": "Muito boa",
                "note": "Requer instalação do Ollama. Recomendado: Qwen 2.5 (7B, ~4GB). Funciona 100% offline.",
                "status": "nao_instalado", "guide_urls": [OLLAMA_DOWNLOAD, OLLAMA_DOCS],
            })

        if keys:
            for k in keys:
                n += 1
                opts.append({
                    "id": f"api_{k['id']}", "num": n,
                    "title": f"{k['label']} (chave detectada!)",
                    "cost": "pago" if k["paid"] else "gratuito",
                    "setup": "Já configurado",
                    "quality": "Excelente" if k["paid"] else "Boa",
                    "note": f"API key {k['env_var']} encontrada.",
                    "status": "chave_detectada", "guide_urls": [],
                })

        if not keys:
            n += 1
            opts.append({
                "id": "api_gemini", "num": n,
                "title": "API Key Gemini (gratuito)",
                "cost": "gratuito", "setup": "Precisa cadastro Google",
                "quality": "Boa",
                "note": "Gemini tem tier gratuito. Precisa de conta Google e chave no AI Studio.",
                "status": "sem_chave", "guide_urls": [GEMINI_SIGNUP],
            })
            n += 1
            opts.append({
                "id": "api_anthropic", "num": n,
                "title": "API Key Claude (Anthropic)",
                "cost": "pago (~US$0,50/dia)", "setup": "Precisa cadastro + cartão",
                "quality": "Excelente",
                "note": "Claude Sonnet é o melhor para ensino. Requer cadastro com cartão.",
                "status": "sem_chave", "guide_urls": [ANTHROPIC_SIGNUP],
            })

        n += 1
        opts.append({
            "id": "stubs", "num": n,
            "title": "Modo offline (stubs básicos)",
            "cost": "gratuito", "setup": "Nenhum",
            "quality": "Basica",
            "note": "Respostas programadas sem IA. Funciona sem internet, sem instalação.",
            "status": "sempre_disponivel", "guide_urls": [],
        })

        return opts
