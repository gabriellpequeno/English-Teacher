"""Harness CLI de exemplo. Qualquer outro harness (API, bot, web) usa o mesmo init()."""

from __future__ import annotations
import argparse
from src.factory import init
from src.registry import registry
from src.orchestrator import orchestrator
from src.setup import SetupManager


def _run_tutorial(agents, state):
    """Interactive tutorial flow for first-run setup."""
    print("\n" + "=" * 56)
    print("  ENGLISH TEACHER — CONFIGURACAO INICIAL")
    print("=" * 56)
    print()
    print(agents["tuto"].process(state, "iniciar"))
    print()
    while True:
        try:
            ui = input("voce > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not ui:
            continue
        if ui in ("/exit", "/quit", "/sair"):
            return False
        resp = agents["tuto"].process(state, ui)
        print(f"\n{resp}\n")
        if resp == "__TUTO_COMPLETE__":
            break
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="Aluno")
    parser.add_argument("--level", default="A1", choices=["A1","A2","B1","B2","C1","C2"])
    parser.add_argument("--target", default="B2", choices=["A1","A2","B1","B2","C1","C2"])
    parser.add_argument("--list", action="store_true", help="Listar agentes e sair")
    parser.add_argument("--setup", action="store_true", help="Forcar tutorial de configuracao")
    args = parser.parse_args()

    agents, state = init(
        learner_name=args.name,
        target_level=args.target,
        context="python",
    )

    if args.list:
        for name, meta in registry.list_meta().items():
            print(f"  {name:<12s} v{meta['version']}  {meta['description'][:60]}")
        return

    setup_mgr = SetupManager(context="python")

    if args.setup or setup_mgr.is_first_run():
        if not _run_tutorial(agents, state):
            return
        setup_mgr = SetupManager(context="python")
        setup_mgr.detect()

    print(f"\nBem-vindo(a), {args.name}! (Nivel: {args.level} -> Alvo: {args.target})")
    print(f"Backend: {setup_mgr.data.get('backend', 'unknown')}")
    print(f"Agentes: {', '.join(registry.list_meta().keys())}")
    print()

    agents["classifier"].process(state, "iniciar")
    print(f"Classifier: {state.interactions[-1].content[:200]}...\n")

    while True:
        try:
            ui = input("voce > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not ui:
            continue
        if ui in ("/exit", "/quit", "/sair"):
            break
        if ui in ("/setup", "/config"):
            agents["tuto"].reset()
            print("\n" + agents["tuto"].process(state, "iniciar"))
            print()
            while True:
                try:
                    sub = input("voce > ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if not sub:
                    continue
                if sub in ("/exit", "/quit", "/sair", "/cancel"):
                    break
                resp = agents["tuto"].process(state, sub)
                print(f"\n{resp}\n")
                if resp == "__TUTO_COMPLETE__":
                    setup_mgr = SetupManager(context="python")
                    setup_mgr.detect()
                    print(f"Backend atualizado: {setup_mgr.data.get('backend', 'unknown')}\n")
                    break
            continue
        if ui == "/help":
            print("Comandos: /agents, /status, /setup, /config, /exit")
            continue
        if ui == "/agents":
            for n, _ in registry.list():
                print(f"  {n}")
            continue
        if ui == "/status":
            print(orchestrator.status(state))
            print(state.summary())
            continue

        resp = orchestrator.route(state, ui)
        print(f"\n{resp}\n")


if __name__ == "__main__":
    main()
