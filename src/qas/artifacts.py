"""Persist configs, provenance, metrics, states, and criteria-derived verdicts."""

import csv
import hashlib
import importlib.metadata
import json
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import yaml


def git(*args: str) -> str | None:
    try:
        return subprocess.check_output(["git", *args], stderr=subprocess.DEVNULL, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def environment(config: dict) -> dict:
    packages = {p.metadata["Name"]: p.version for p in importlib.metadata.distributions()}
    gpu: dict = {"available": False, "cuda": None}
    try:
        import torch

        gpu = {"available": torch.cuda.is_available(), "cuda": torch.version.cuda}
    except ImportError:
        pass
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "cpu": platform.processor(),
        "gpu": gpu,
        "packages": packages,
        "git_sha": git("rev-parse", "HEAD"),
        "git_dirty": bool(git("status", "--porcelain")),
        "timestamp": datetime.now(UTC).isoformat(),
        "config_sha256": hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(),
    }


def create(root: str | Path, config: dict) -> Path:
    import re

    if not isinstance(config.get("experiment_id"), str) or not re.fullmatch(
        r"[a-z0-9][a-z0-9-]{0,63}", config["experiment_id"]
    ):
        raise ValueError("Unsafe experiment identifier")
    run = (
        Path(root)
        / config["experiment_id"]
        / (datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8])
    )
    run.mkdir(parents=True, exist_ok=False)
    (run / "checkpoints").mkdir()
    (run / "figures").mkdir()
    (run / "config.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")
    (run / "environment.json").write_text(
        json.dumps(environment(config), indent=2), encoding="utf-8"
    )
    return run


def write_results(run: Path, rows: list[dict], config: dict) -> None:
    from qas.metrics import statistics

    grouped = []
    for n in config["qubits"]:
        for method in ("exact", "nqs", "vqe"):
            selected = [r for r in rows if r["qubits"] == n and r["method"] == method]
            if selected:
                grouped.append(
                    {
                        "qubits": n,
                        "method": method,
                        **{
                            metric: statistics([r[metric] for r in selected])
                            for metric in ("absolute_energy_error", "fidelity", "runtime_seconds")
                        },
                    }
                )
    expected = {(n, "exact", None) for n in config["qubits"]} | {
        (n, method, seed)
        for n in config["qubits"]
        for method in ("nqs", "vqe")
        for seed in config["seeds"]
    }
    observed = [(r["qubits"], r["method"], r.get("seed")) for r in rows]
    complete = set(observed) == expected and len(observed) == len(expected)
    checks = [
        r["absolute_energy_error"] <= config["energy_error_max"]
        and r["fidelity"] >= config["fidelity_min"]
        for r in rows
        if r["method"] != "exact"
    ]
    verdict = "INCONCLUSIVE" if not complete else ("SUPPORTED" if all(checks) else "NOT_SUPPORTED")
    payload = {"rows": rows, "seed_statistics": grouped, "verdict": verdict, "complete": complete}
    (run / "metrics.json").write_text(
        json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8"
    )
    keys = sorted(set().union(*(row.keys() for row in rows)) - {"history"})
    with (run / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    report = f"# Verdict: {verdict}\n\nHypothesis: both approximations meet the registered accuracy thresholds at every size and seed.\n\nBaseline: dense exact diagonalisation.\n\nCriteria: absolute energy error <= {config['energy_error_max']}; fidelity >= {config['fidelity_min']}.\n\nPassed: {sum(checks)}/{len(checks)} stochastic evaluations. Complete contract: {complete}.\n\nEvidence level: BENCHMARKED. Accuracy support does not establish computational or quantum advantage.\n\nLimitations: exact enumeration RBM, noiseless state-vector VQE, finite seeds, CPU timings include setup; tracemalloc excludes native allocations. Degenerate-state fidelity depends on selected eigenvector.\n\n## Seed statistics\n\n```json\n{json.dumps(grouped, indent=2)}\n```\n"
    (run / "verdict.md").write_text(report, encoding="utf-8")
