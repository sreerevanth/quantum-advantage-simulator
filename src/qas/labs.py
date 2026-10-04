"""Configured secondary experiments; separate from the Phase-1 evidence contract."""

import csv
import json
import time
from pathlib import Path

import numpy as np
import yaml

from qas import artifacts, discovery, exact, noise, variational


def load(path: str | Path) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    allowed = {
        "experiment_id",
        "kind",
        "qubits",
        "seeds",
        "probabilities",
        "scales",
        "channel",
        "edges",
        "depth",
        "iterations",
        "budget",
        "max_gates",
        "penalty",
        "preparation",
        "vqe_depth",
        "vqe_iterations",
    }
    if not isinstance(data, dict) or set(data) - allowed:
        raise ValueError("Lab config must be a mapping with recognized keys")
    if data.get("kind") not in ("noise", "mitigate", "qaoa", "discover"):
        raise ValueError("Unknown lab kind")
    relevant = {"experiment_id", "kind", "qubits", "seeds"} | {
        "noise": {
            "probabilities",
            "scales",
            "channel",
            "preparation",
            "vqe_depth",
            "vqe_iterations",
        },
        "mitigate": {
            "probabilities",
            "scales",
            "channel",
            "preparation",
            "vqe_depth",
            "vqe_iterations",
        },
        "qaoa": {"edges", "depth", "iterations"},
        "discover": {"budget", "max_gates", "penalty"},
    }[data["kind"]]
    if set(data) - relevant:
        raise ValueError("Configuration includes fields unrelated to this lab")
    if type(data.get("qubits")) is not int or not 2 <= data["qubits"] <= 8:
        raise ValueError("Lab qubits must be integer 2–8")
    seeds = data.get("seeds", [0])
    if (
        not isinstance(seeds, list)
        or not seeds
        or len(set(seeds)) != len(seeds)
        or any(type(s) is not int or not 0 <= s < 2**32 for s in seeds)
    ):
        raise ValueError("Invalid lab seed list")
    data["seeds"] = seeds
    if data["kind"] == "qaoa":
        edges = data.get("edges", [[i, i + 1] for i in range(data["qubits"] - 1)])
        if (
            not isinstance(edges, list)
            or not edges
            or any(
                not isinstance(e, list)
                or len(e) != 2
                or any(type(v) is not int or not 0 <= v < data["qubits"] for v in e)
                or e[0] == e[1]
                for e in edges
            )
            or len({tuple(sorted(e)) for e in edges}) != len(edges)
        ):
            raise ValueError("Invalid or duplicate graph edges")
    if "penalty" in data and (
        not isinstance(data["penalty"], (int, float))
        or not np.isfinite(data["penalty"])
        or data["penalty"] < 0
    ):
        raise ValueError("Invalid discovery penalty")
    for field in ("depth", "iterations", "budget", "max_gates", "vqe_depth", "vqe_iterations"):
        if field in data and (type(data[field]) is not int or not 1 <= data[field] <= 10000):
            raise ValueError(f"Invalid {field}")
    if data["kind"] in ("noise", "mitigate"):
        if data.get("preparation", "exact") not in ("exact", "vqe"):
            raise ValueError("Noise preparation must be exact or vqe")
        probabilities = data.get("probabilities", [0.05])
        scales = data.get("scales", [1, 2, 3])
        if (
            not isinstance(probabilities, list)
            or not probabilities
            or not isinstance(scales, list)
            or len(scales) < 2
            or len(set(scales)) != len(scales)
            or any(not isinstance(x, (float, int)) or not np.isfinite(x) or x < 1 for x in scales)
            or any(
                not isinstance(p, (float, int))
                or not np.isfinite(p)
                or not 0 <= p * max(scales) <= 1
                for p in probabilities
            )
        ):
            raise ValueError("Invalid noise probabilities/scales")
        if data.get("channel", "depolarizing") not in ("depolarizing", "bit_flip"):
            raise ValueError("TFIM lab supports depolarizing or bit_flip")
    return data


def run(config: dict, root: str | Path = "results/labs") -> Path:
    directory = artifacts.create(root, config)
    rows = []
    n = config["qubits"]
    if config["kind"] in ("noise", "mitigate"):
        ham = exact.hamiltonian(n)
        ground = exact.solve(ham)[1][:, 0]
        for seed in config["seeds"] if config.get("preparation") == "vqe" else [None]:
            state = ground
            if seed is not None:
                state = variational.vqe(
                    ham, n, seed, config.get("vqe_depth", 3), config.get("vqe_iterations", 100)
                )["state"]
            for probability in config.get("probabilities", [0.05]):
                row = noise.experiment(
                    state,
                    ham,
                    n,
                    probability,
                    tuple(config.get("scales", [1, 2, 3])),
                    config.get("channel", "depolarizing"),
                )
                row.update(
                    {
                        "seed": seed,
                        "preparation": config.get("preparation", "exact"),
                        "exact_ground_energy": exact.expectation(ground, ham),
                        "prepared_energy_error": abs(row["ideal"] - exact.expectation(ground, ham)),
                    }
                )
                rows.append(row)
        verdict = "SUPPORTED" if all(r["improvement"] > 0 for r in rows) else "NOT_SUPPORTED"
        hypothesis = "Richardson extrapolation strictly reduces analytic error at every configured noise probability."
    else:
        for seed in config["seeds"]:
            start = time.perf_counter()
            if config["kind"] == "qaoa":
                row = variational.qaoa(
                    n,
                    config.get("edges", [[i, i + 1] for i in range(n - 1)]),
                    seed,
                    config.get("depth", 2),
                    config.get("iterations", 100),
                )
            else:
                target = discovery.execute(
                    [discovery.Gate("H", 0), discovery.Gate("CNOT", 0, 1)], n
                )
                row = discovery.search(
                    target,
                    n,
                    seed,
                    config.get("budget", 200),
                    config.get("max_gates", 8),
                    config.get("penalty", 0.001),
                )
            rows.append({"seed": seed, "runtime_seconds": time.perf_counter() - start, **row})
        verdict = "BENCHMARKED"
        hypothesis = "Exploratory baseline comparison; no advantage hypothesis registered."
    (directory / "metrics.json").write_text(
        json.dumps({"rows": rows, "verdict": verdict}, indent=2, allow_nan=False), encoding="utf-8"
    )
    flat = [
        {k: v for k, v in row.items() if isinstance(v, (str, int, float)) or v is None}
        for row in rows
    ]
    with (directory / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted(set().union(*(r.keys() for r in flat))))
        writer.writeheader()
        writer.writerows(flat)
    (directory / "stdout.log").write_text(
        f"Executed {len(rows)} configurations\n", encoding="utf-8"
    )
    (directory / "verdict.md").write_text(
        f"# {verdict}\n\n{hypothesis}\n\nBaseline: exact analytic expectations / exhaustive MaxCut / random search and fixed Bell circuit as applicable.\n\nLimitations: ideal classical simulation, finite budgets/seeds, no QPU or sampled ZNE evidence.\n",
        encoding="utf-8",
    )
    if config["kind"] in ("noise", "mitigate"):
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
        for name in ("raw_error", "mitigated_error"):
            ax.plot(
                [r["probability"] for r in rows], [r[name] for r in rows], marker="o", label=name
            )
        ax.set(xlabel="Local channel probability", ylabel="Absolute energy error")
        ax.legend()
        for extension in ("png", "svg"):
            fig.savefig(directory / "figures" / f"noise_errors.{extension}", dpi=200)
        plt.close(fig)
    return directory
