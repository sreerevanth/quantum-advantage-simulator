"""Plot only persisted measurements; never embed scientific results."""

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot(run: str | Path) -> list[Path]:
    run = Path(run)
    rows = json.loads((run / "metrics.json").read_text())["rows"]
    output = run / "figures"
    output.mkdir(exist_ok=True)
    paths = []
    for metric in (
        "absolute_energy_error",
        "fidelity",
        "runtime_seconds",
        "python_peak_bytes",
        "magnetization_error",
        "transverse_magnetization_error",
    ):
        fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
        for method in ("exact", "nqs", "vqe"):
            selected = [r for r in rows if r["method"] == method]
            ns = sorted({r["qubits"] for r in selected})
            values = [[r[metric] for r in selected if r["qubits"] == n] for n in ns]
            ax.errorbar(
                ns,
                [np.mean(v) for v in values],
                yerr=[np.std(v, ddof=1) if len(v) > 1 else 0 for v in values],
                marker="o",
                capsize=3,
                label=method,
            )
        ax.set(xlabel="Qubits", ylabel=metric.replace("_", " "))
        ax.set_xticks(sorted({r["qubits"] for r in rows}))
        ax.legend()
        ax.grid(alpha=0.2)
        for suffix in ("png", "svg"):
            path = output / f"{metric}.{suffix}"
            fig.savefig(path, dpi=200)
            paths.append(path)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 4), layout="constrained")
    for row in rows:
        if row.get("history"):
            ax.plot(
                row["history"],
                alpha=0.6,
                label=f"{row['method']} n={row['qubits']} s={row['seed']}",
            )
    ax.set(xlabel="Optimizer step", ylabel="Energy", title="Persisted optimization histories")
    fig.savefig(output / "convergence.png", dpi=200)
    plt.close(fig)
    for n in sorted({r["qubits"] for r in rows}):
        for method in ("nqs", "vqe"):
            selected = [r for r in rows if r["qubits"] == n and r["method"] == method]
            if not selected:
                continue
            fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
            for row in selected:
                ax.plot(row["history"], label=f"seed {row['seed']}")
            ax.axhline(selected[0]["exact_energy"], color="black", linestyle="--", label="exact")
            ax.set(xlabel="Optimizer step", ylabel="Energy", title=f"{method.upper()}, {n} qubits")
            ax.legend()
            for suffix in ("png", "svg"):
                path = output / f"{method}_convergence_{n}.{suffix}"
                fig.savefig(path, dpi=200)
                paths.append(path)
            plt.close(fig)
    return paths


def summarize(root: str | Path, output: str | Path) -> Path:
    records: list[dict] = []
    for file in Path(root).rglob("summary.csv"):
        with file.open(encoding="utf-8") as handle:
            records.extend({"run": str(file.parent), **row} for row in csv.DictReader(handle))
    if not records:
        raise ValueError("No persisted summaries found")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=sorted(set().union(*(r.keys() for r in records)))
        )
        writer.writeheader()
        writer.writerows(records)
    return output
