"""Harness CLI de exemplo. Qualquer outro harness (API, bot, web) usa o mesmo init()."""

from __future__ import annotations
import argparse
from src.factory import init
from src.registry import registry
from src.orchestrator import orchestrator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="Aluno")
    parser.add_argument("--level", default="A1", choices=["A1","A2","B1","B2","C1","C2"])
    parser.add_argument("--target", default="B2", choices=["A1","A2","B1","B2","C1","C2"])
    parser.add_argument("--list", action="store_true", help="Listar agentes e sair")
    args = parser.parse_args()

    agents, state = init(
        learner_name=args.name,
        target_level=args.target,
    )

    if args.list:
        for name, meta in registry.list_meta().items():
            print(f"  {name:<12s} v{meta['version']}  {meta['description'][:60]}")
        return

    print(f"Bem-vindo(a), {args.name}! (Nivel: {args.level} -> Alvo: {args.target})")
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
        if ui == "/help":
            print("Comandos: /agents, /status, /exit")
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
