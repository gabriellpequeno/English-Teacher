from __future__ import annotations
from src.agents.base import BaseAgent
from src.state import LearnerState
from src.setup import SetupManager


class SetupTutor(BaseAgent):
    name = "tuto"
    description = "Tutor de configuracao — guia o usuario na escolha do backend"
    version = "1.0.0"
    tags = ["setup", "config", "tutorial"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_manager: SetupManager = kwargs.get("setup_manager")
        self._step: str = "welcome"
        self._chosen: str | None = None

    def build_system_prompt(self) -> str:
        return "Tutor de configuracao do English Teacher. Ajuda o usuario a escolher e configurar o backend ideal."

    def process(self, state: LearnerState, user_input: str) -> str:
        state.add_interaction("learner", self.name, user_input)
        response = self._handle(state, user_input)
        state.add_interaction("agent", self.name, response)
        return response

    def reset(self) -> None:
        self._step = "welcome"
        self._chosen = None

    def is_complete(self) -> bool:
        return self._step == "complete"

    def _handle(self, state: LearnerState, user_input: str) -> str:
        if not self._should_skip_reconfig(state, user_input):
            if user_input in ("/setup", "/config", "reconfigurar", "reconfig"):
                self.reset()
                return self._welcome(state)

        if user_input in ("iniciar", "start", "comecar"):
            self._step = "welcome"
            return self._welcome(state)

        if self._step == "welcome":
            return self._handle_menu(state, user_input)
        if self._step.startswith("ollama_"):
            return self._handle_ollama(state, user_input)
        if self._step.startswith("api_"):
            return self._handle_api(state, user_input)
        if self._step == "native":
            return self._handle_native(state, user_input)
        if self._step == "stubs":
            return self._handle_stubs(state, user_input)
        if self._step == "complete":
            return "__TUTO_COMPLETE__"
        return self._welcome(state)

    def _should_skip_reconfig(self, state, user_input):
        return self._step in ("ollama_install", "ollama_start", "ollama_download", "ollama_custom_model", "ollama_test")

    def _welcome(self, state: LearnerState) -> str:
        self.setup_manager.detect()
        options = self.setup_manager.get_options()
        lines = [
            "=" * 56,
            "  BEM-VINDO AO ENGLISH TEACHER!",
            "=" * 56,
            "",
            "Antes de comecarmos, vamos configurar o sistema.",
            "Escolha como voce quer que o English Teacher funcione:",
            "",
        ]
        for opt in options:
            status_icon = {"disponivel": "[+]", "rodando": "[+]", "parado": "[!]",
                           "nao_instalado": "[X]", "chave_detectada": "[+]",
                           "sem_chave": "[X]", "sempre_disponivel": "[+]"}
            icon = status_icon.get(opt["status"], "[?]")
            lines.append(f"  [{opt['num']}] {icon} {opt['title']}")
            lines.append(f"      Qualidade: {opt['quality']}  |  Custo: {opt['cost']}  |  {opt['setup']}")
            lines.append(f"      {opt['note'][:80]}")
            lines.append("")
        lines.append("-" * 56)
        lines.append("Digite o NUMERO da opcao desejada:")
        return "\n".join(lines)

    def _handle_menu(self, state: LearnerState, user_input: str) -> str:
        options = self.setup_manager.get_options()
        choice = user_input.strip()
        selected = None
        for opt in options:
            if choice == str(opt["num"]) or choice == opt["id"]:
                selected = opt
                break
        if not selected:
            return f"Opcao invalida. Escolha um numero entre 1 e {len(options)}.\n\n" + self._welcome(state)

        self._chosen = selected["id"]
        if selected["id"] == "native":
            self._step = "native"
            return self._native_info(state)
        if selected["id"] == "ollama":
            self._step = "ollama_check"
            return self._ollama_check(state)
        if selected["id"].startswith("api_"):
            self._step = selected["id"]
            return self._api_guide(state, selected["id"])
        if selected["id"] == "stubs":
            self._step = "stubs"
            return self._stubs_info(state)
        return self._welcome(state)

    def _native_info(self, state: LearnerState) -> str:
        return (
            "=" * 56 + "\n"
            "  MODO NATIVO OPENCODE\n"
            "=" * 56 + "\n\n"
            "O English Teacher usa o modelo padrao do opencode CLI.\n"
            "Voce NAO precisa instalar nada.\n\n"
            "Vantagens:\n"
            "  • Zero instalacao\n"
            "  • Zero configuracao\n"
            "  • Funciona imediatamente\n\n"
            "Limitacoes:\n"
            "  • Todos os agentes usam o MESMO modelo\n"
            "  • Depende do opencode CLI (nao funciona com python -m src.main)\n"
            "  • Qualidade depende do modelo que o opencode estiver usando\n\n"
            "Digite CONFIRMAR para salvar ou VOLTAR para o menu."
        )

    def _handle_native(self, state: LearnerState, user_input: str) -> str:
        if user_input.lower() in ("confirmar", "sim", "ok", "yes"):
            self.setup_manager.mark_configured(backend="native", tuto_completed_steps=["welcome", "native_confirm"])
            self._step = "complete"
            return self._completion_message()
        if user_input.lower() in ("voltar", "back", "menu", "nao"):
            self._step = "welcome"
            return self._welcome(state)
        return "Digite CONFIRMAR para salvar ou VOLTAR para o menu."

    def _ollama_check(self, state: LearnerState) -> str:
        api = self.setup_manager.data.get("ollama_available", False)
        bin_path = self.setup_manager.data.get("ollama_installed")
        lines = ["=" * 56, "  OLLAMA + MODELO LOCAL", "=" * 56, ""]

        if api:
            lines += [
                "[OK] Servidor Ollama rodando em http://localhost:11434!",
                "",
                "Agora vamos escolher um modelo para baixar.",
                "",
                "Modelos recomendados:",
                "  [1] Qwen 2.5 (7B)  — Melhor custo-beneficio, ~4GB RAM",
                "  [2] Llama 3.2 (3B) — Mais leve, ~2GB RAM",
                "  [3] Phi-4 (14B)    — Mais preciso, ~8GB RAM",
                "  [4] Outro modelo (voce escolhe)",
                "",
                "Digite o numero do modelo desejado:",
            ]
            self._step = "ollama_pull"
        elif bin_path:
            lines += [
                f"[!] Ollama instalado em: {bin_path}",
                "Mas o servidor nao esta rodando.",
                "",
                "Para iniciar, abra um terminal e execute:",
                "  ollama serve",
                "",
                "Depois volte aqui e digite PRONTO.",
            ]
            self._step = "ollama_start"
        else:
            lines += [
                "[X] Ollama nao instalado.",
                "",
                "Guia de instalacao rapida:",
                "",
                "  Windows:",
                "    1. Baixe: https://ollama.com/download/windows",
                "    2. Execute o instalador (inicia automaticamente)",
                "",
                "  Linux:",
                "    curl -fsSL https://ollama.com/install.sh | sh",
                "",
                "  macOS:",
                "    Baixe o .dmg em https://ollama.com/download/mac",
                "",
                "Apos instalar, volte e digite PRONTO.",
            ]
            self._step = "ollama_install"
        return "\n".join(lines)

    def _handle_ollama(self, state: LearnerState, user_input: str) -> str:
        step = self._step

        if step == "ollama_install":
            if user_input.lower() in ("pronto", "done", "instalei", "ok"):
                self.setup_manager.detect()
                if self.setup_manager.data.get("ollama_available"):
                    self._step = "ollama_pull"
                    return "Perfeito! Ollama ja esta rodando.\n\n" + self._ollama_check(state)
                if self.setup_manager.data.get("ollama_installed"):
                    self._step = "ollama_start"
                    return "Instalado! Agora precisa iniciar o servidor.\n\n" + self._ollama_check(state)
                return (
                    "Ainda nao detectei o Ollama. Verifique:\n"
                    "  • A instalacao foi concluida?\n"
                    "  • Tente reiniciar o terminal\n\n"
                    "Digite PRONTO quando tiver instalado, ou VOLTAR."
                )
            if user_input.lower() in ("voltar", "back", "menu", "nao"):
                self._step = "welcome"
                return self._welcome(state)
            return "Digite PRONTO quando a instalacao terminar, ou VOLTAR."

        if step == "ollama_start":
            if user_input.lower() in ("pronto", "done", "ok"):
                self.setup_manager.detect()
                if self.setup_manager.data.get("ollama_available"):
                    self._step = "ollama_pull"
                    return "Servidor detectado!\n\n" + self._ollama_check(state)
                return "Ainda sem conexao. Execute 'ollama serve' e digite PRONTO, ou VOLTAR."
            if user_input.lower() in ("voltar", "back", "menu"):
                self._step = "welcome"
                return self._welcome(state)
            return "Digite PRONTO quando o servidor estiver rodando, ou VOLTAR."

        if step == "ollama_pull":
            model_map = {"1": "qwen2.5:7b", "2": "llama3.2:3b", "3": "phi4:latest"}
            model = model_map.get(user_input.strip())
            if model:
                self.setup_manager.data["ollama_model"] = model
                self._step = "ollama_download"
                return (
                    f"Baixe o modelo executando no terminal:\n"
                    f"  ollama pull {model}\n\n"
                    f"Tamanho aproximado: qwen2.5:7b ~4GB | llama3.2:3b ~2GB | phi4 ~9GB\n\n"
                    f"Digite PRONTO quando o download terminar."
                )
            if user_input.strip() == "4":
                self._step = "ollama_custom_model"
                return (
                    "Digite o nome do modelo que deseja baixar.\n"
                    "Ex: mistral, gemma2:9b, deepseek-coder:6.7b\n"
                    "Lista completa: https://ollama.com/library\n\n"
                    "Ou digite VOLTAR."
                )
            return "Escolha 1, 2, 3 ou 4. Ou VOLTAR."

        if step == "ollama_custom_model":
            if user_input.strip() and user_input.lower() not in ("voltar", "back"):
                self.setup_manager.data["ollama_model"] = user_input.strip()
                self._step = "ollama_download"
                return (
                    f"Execute no terminal:\n"
                    f"  ollama pull {user_input.strip()}\n\n"
                    f"Digite PRONTO quando terminar."
                )
            self._step = "ollama_pull"
            return self._ollama_check(state)

        if step == "ollama_download":
            if user_input.lower() in ("pronto", "done", "ok", "baixou"):
                self._step = "ollama_test"
                model = self.setup_manager.data.get("ollama_model", "qwen2.5:7b")
                api_ok = self.setup_manager.data.get("ollama_available", False)
                return (
                    "=" * 56 + "\n"
                    "  TESTE DO OLLAMA\n"
                    "=" * 56 + "\n\n"
                    f"Servidor: {'[OK] Rodando' if api_ok else '[X] Parado'}\n"
                    f"Modelo: {model}\n\n"
                    "Para testar manualmente, execute:\n"
                    f"  ollama run {model}\n\n"
                    "Digite CONFIRMAR para salvar ou VOLTAR."
                )
            if user_input.lower() in ("voltar", "back", "menu"):
                self._step = "ollama_pull"
                return self._ollama_check(state)
            return "Digite PRONTO quando o download terminar, ou VOLTAR."

        if step == "ollama_test":
            if user_input.lower() in ("confirmar", "sim", "ok"):
                self.setup_manager.mark_configured(
                    backend="ollama",
                    ollama_model=self.setup_manager.data.get("ollama_model", "qwen2.5:7b"),
                    tuto_completed_steps=["welcome", "ollama_install", "ollama_pull", "ollama_test"],
                )
                self._step = "complete"
                return self._completion_message()
            if user_input.lower() in ("voltar", "back", "menu", "nao"):
                self._step = "welcome"
                return self._welcome(state)
            return "Digite CONFIRMAR para salvar ou VOLTAR."

        return self._welcome(state)

    def _api_guide(self, state: LearnerState, api_id: str) -> str:
        guides = {
            "api_gemini": {
                "title": "API Gemini (Gratuito)",
                "steps": [
                    "1. Acesse: https://aistudio.google.com/apikey",
                    "2. Faca login com sua conta Google",
                    "3. Clique em 'Create API Key'",
                    "4. Copie a chave gerada",
                    "",
                    "Configurar variavel de ambiente:",
                    "",
                    "  PowerShell:",
                    '    $env:GOOGLE_API_KEY = "sua-chave-aqui"',
                    "",
                    "  Linux/macOS:",
                    '    export GOOGLE_API_KEY="sua-chave-aqui"',
                    "",
                    "Digite PRONTO quando tiver configurado.",
                ],
            },
            "api_anthropic": {
                "title": "API Claude (Anthropic — Pago)",
                "steps": [
                    "[!] Claude e um servico PAGO (~US$0,50/dia).",
                    "",
                    "1. Acesse: https://console.anthropic.com/",
                    "2. Crie conta (precisa de cartao)",
                    "3. Va em 'API Keys' e crie uma chave",
                    "4. Copie a chave (comeca com 'sk-ant-')",
                    "",
                    "Configurar variavel de ambiente:",
                    "",
                    "  PowerShell:",
                    '    $env:ANTHROPIC_API_KEY = "sk-ant-sua-chave"',
                    "",
                    "  Linux/macOS:",
                    '    export ANTHROPIC_API_KEY="sk-ant-sua-chave"',
                    "",
                    "Digite PRONTO quando tiver configurado.",
                ],
            },
        }
        guide = guides.get(api_id)
        if not guide:
            return "Opcao nao encontrada."
        self._step = api_id
        lines = ["=" * 56, f"  {guide['title']}", "=" * 56, ""]
        lines.extend(guide["steps"])
        return "\n".join(lines)

    def _handle_api(self, state: LearnerState, user_input: str) -> str:
        if user_input.lower() in ("pronto", "done", "configurei"):
            self.setup_manager.detect()
            keys = self.setup_manager.data.get("api_key_providers", [])
            key_ids = [k["id"] for k in keys]
            api_type = self._step.replace("api_", "")
            if api_type in key_ids:
                self.setup_manager.mark_configured(
                    backend=f"api_{api_type}",
                    tuto_completed_steps=["welcome", f"api_{api_type}_confirm"],
                )
                self._step = "complete"
                return self._completion_message()
            return (
                f"Ainda nao detectei a chave. Verifique:\n"
                f"  • A variavel de ambiente foi configurada?\n"
                f"  • Reiniciou o terminal apos configurar?\n\n"
                f"Digite PRONTO quando configurado, ou VOLTAR."
            )
        if user_input.lower() in ("voltar", "back", "menu"):
            self._step = "welcome"
            return self._welcome(state)
        return "Digite PRONTO quando a chave estiver configurada, ou VOLTAR."

    def _stubs_info(self, state: LearnerState) -> str:
        return (
            "=" * 56 + "\n"
            "  MODO OFFLINE (STUBS BASICOS)\n"
            "=" * 56 + "\n\n"
            "[!] Limitacoes:\n"
            "  • Respostas fixas e previsiveis\n"
            "  • Nao adapta ao nivel do aluno\n"
            "  • Apenas para testar a estrutura\n\n"
            "[+] Vantagens:\n"
            "  • Funciona 100% offline\n"
            "  • Zero dependencias\n"
            "  • Inicializacao instantanea\n\n"
            "Recomendo apenas para testes rapidos.\n"
            "Para aprendizado real, escolha Ollama ou Native.\n\n"
            "Digite CONFIRMAR para salvar ou VOLTAR."
        )

    def _handle_stubs(self, state: LearnerState, user_input: str) -> str:
        if user_input.lower() in ("confirmar", "sim", "ok"):
            self.setup_manager.mark_configured(backend="stubs", tuto_completed_steps=["welcome", "stubs_confirm"])
            self._step = "complete"
            return self._completion_message()
        if user_input.lower() in ("voltar", "back", "menu", "nao"):
            self._step = "welcome"
            return self._welcome(state)
        return "Digite CONFIRMAR para salvar ou VOLTAR."

    def _completion_message(self) -> str:
        backend = self.setup_manager.data.get("backend", "unknown")
        return (
            "=" * 56 + "\n"
            "  CONFIGURACAO CONCLUIDA!\n"
            "=" * 56 + f"\n\n"
            f"Backend: {backend}\n\n"
            "Voce pode reconfigurar a qualquer momento digitando /setup ou /config.\n"
            "Pressione ENTER para comecar a aprender ingles!"
        )
