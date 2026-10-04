"""Command line interface for bounded local scientific experiments."""

import argparse
import json
import sys
from pathlib import Path

from qas.config import load


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("exact", "nqs", "vqe", "benchmark"):
        p = sub.add_parser(name, help=f"Run {name} TFIM with provenance")
        p.add_argument("--config", required=True)
        p.add_argument("--output", default="results/runs")
    for name in ("noise", "mitigate", "qaoa", "discover"):
        p = sub.add_parser(name, help=f"Run local {name} experiment")
        p.add_argument("--config", help="Validated YAML lab configuration")
        p.add_argument("--qubits", type=int, default=2)
        p.add_argument("--seed", type=int, default=0)
        p.add_argument("--output", default="results/labs")
        if name in ("noise", "mitigate"):
            p.add_argument("--probability", type=float, default=0.05)
            p.add_argument("--kind", choices=["depolarizing", "bit_flip"], default="depolarizing")
            p.add_argument("--scales", nargs="+", type=float, default=[1, 2, 3])
        if name in ("qaoa", "discover"):
            p.add_argument("--budget", type=int, default=100)
    p = sub.add_parser("experiment", help="Inspect or run the registry")
    p.add_argument("action", choices=["list", "inspect", "run"])
    p.add_argument("id", nargs="?")
    p.add_argument("--registry", default="experiments/registry.yaml")
    p = sub.add_parser("results", help="Plot or combine stored artifacts")
    p.add_argument("action", choices=["plot", "summarize"])
    p.add_argument("path")
    p.add_argument("--output", default="results/tables/combined.csv")
    sub.add_parser("doctor", help="Report environment and optional dependencies")
    sub.add_parser("validate", help="Run installed scientific validation suite")
    args = parser.parse_args(argv)
    try:
        if args.command in ("exact", "nqs", "vqe", "benchmark"):
            from qas.benchmarks.tfim_compare import run

            methods = ("exact", "nqs", "vqe") if args.command == "benchmark" else (args.command,)
            print(run(load(args.config), args.output, methods))
        elif args.command == "experiment":
            from qas.registry import read

            entries = read(args.registry)
            if args.action == "list":
                print(json.dumps(entries, indent=2))
            else:
                entry = next((e for e in entries if e["id"] == args.id), None)
                if entry is None:
                    raise ValueError("Unknown experiment ID")
                if args.action == "inspect":
                    print(json.dumps(entry, indent=2))
                else:
                    from qas.benchmarks.tfim_compare import run

                    print(run(load(Path(args.registry).parent.parent / entry["configuration"])))
        elif args.command == "results":
            from qas.plotting import plot, summarize

            print(plot(args.path) if args.action == "plot" else summarize(args.path, args.output))
        elif args.command == "doctor":
            from qas.artifacts import environment

            print(json.dumps(environment({}), indent=2))
        elif args.command == "validate":
            import pytest

            return pytest.main(["tests", "-q"])
        else:
            if args.config:
                from qas import labs

                config = labs.load(args.config)
                if config["kind"] != args.command:
                    raise ValueError("Lab config kind must match command")
                print(labs.run(config, args.output))
                return 0
            from qas import artifacts, discovery, exact, noise, variational

            if not 2 <= args.qubits <= 8:
                raise ValueError("Local labs support 2–8 qubits")
            config = vars(args).copy()
            config["experiment_id"] = args.command + "-lab"
            directory = artifacts.create(args.output, config)
            n = args.qubits
            if args.command in ("noise", "mitigate"):
                ham = exact.hamiltonian(n)
                state = exact.solve(ham)[1][:, 0]
                result = noise.experiment(
                    state, ham, n, args.probability, tuple(args.scales), args.kind
                )
            elif args.command == "qaoa":
                result = variational.qaoa(
                    n, [[i, i + 1] for i in range(n - 1)], args.seed, iterations=args.budget
                )
            else:
                state = discovery.execute([discovery.Gate("H", 0), discovery.Gate("CNOT", 0, 1)], n)
                result = discovery.search(state, n, args.seed, args.budget)
            (directory / "metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
            (directory / "stdout.log").write_text("Local analytic simulator experiment completed\n")
            (directory / "verdict.md").write_text(
                "# Exploratory lab\n\n"
                + result.get("verdict", "BENCHMARKED")
                + "\n\nNo general advantage claim. Results are in metrics.json.\n"
            )
            print(directory)
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"qas: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
