"""Create secondary tables and figures exclusively from stored lab records."""

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

for file in Path("results/labs").glob("*/*/metrics.json"):
    rows = json.loads(file.read_text())["rows"]
    directory = file.parent / "figures"
    directory.mkdir(exist_ok=True)
    if "random" in rows[0]:
        flat = []
        fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
        for method, color in [("random", "tab:blue"), ("evolutionary", "tab:orange")]:
            for index, row in enumerate(rows):
                data = row[method]
                ax.plot(
                    data["history"], color=color, alpha=0.6, label=method if index == 0 else None
                )
                flat.append(
                    {
                        "seed": row["seed"],
                        "method": method,
                        **{
                            k: data[k]
                            for k in ("fidelity", "score", "gate_count", "depth", "evaluations")
                        },
                    }
                )
        ax.set(
            xlabel="Fitness evaluations",
            ylabel="Best penalized fidelity",
            title="Equal-budget circuit search",
        )
        ax.legend()
        for suffix in ("png", "svg"):
            fig.savefig(directory / f"search_convergence.{suffix}", dpi=200)
        plt.close(fig)
        with (file.parent / "search_summary.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(flat[0]))
            writer.writeheader()
            writer.writerows(flat)
        for metric in ("gate_count", "depth"):
            fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
            for method in ("random", "evolutionary"):
                selected = [r for r in flat if r["method"] == method]
                ax.scatter(
                    [r[metric] for r in selected],
                    [r["fidelity"] for r in selected],
                    label=method,
                    alpha=0.6,
                )
            human = rows[0]["human_bell_baseline"]
            ax.scatter(
                [human[metric]],
                [human["fidelity"]],
                marker="*",
                s=120,
                label="fixed human Bell circuit",
            )
            ax.set(xlabel=metric.replace("_", " "), ylabel="Fidelity", ylim=(0, 1.05))
            ax.legend()
            for suffix in ("png", "svg"):
                fig.savefig(directory / f"{metric}_fidelity.{suffix}", dpi=200)
            plt.close(fig)
    elif "approximation_ratio" in rows[0]:
        fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
        ax.scatter([r["seed"] for r in rows], [r["approximation_ratio"] for r in rows])
        ax.axhline(1, color="black", linestyle="--", label="exact optimum")
        ax.set(xlabel="Seed", ylabel="Expected cut / exact maximum cut", ylim=(0, 1.05))
        ax.set_xticks([r["seed"] for r in rows])
        ax.legend()
        for suffix in ("png", "svg"):
            fig.savefig(directory / f"qaoa_seed_quality.{suffix}", dpi=200)
        plt.close(fig)
print("Secondary figures generated from persisted evidence")
