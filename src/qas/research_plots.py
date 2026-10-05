"""Static publication exports generated exclusively from recorded research rows."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot(directory, rows):
    folder = directory / "figures"
    folder.mkdir(exist_ok=True)

    def save(name):
        plt.tight_layout()
        for suffix in ("png", "svg", "pdf"):
            plt.savefig(folder / f"{name}.{suffix}", dpi=160)
        plt.close()

    neural = [r for r in rows if r["kind"] == "nqs"]
    if neural:
        plt.figure(figsize=(7, 4))
        for model in sorted({r["model"] for r in neural}):
            subset = [r for r in neural if r["model"] == model]
            plt.scatter(
                [r["qubits"] for r in subset],
                [r["absolute_energy_error"] for r in subset],
                label=model,
                alpha=0.65,
            )
        plt.yscale("symlog", linthresh=1e-8)
        plt.xlabel("Qubits")
        plt.ylabel("Absolute energy error")
        plt.legend()
        save("nqs-seed-distributions")
    vqe = [r for r in rows if r["kind"] == "vqe"]
    if vqe:
        plt.figure(figsize=(9, 4))
        labels = sorted({r["variant"] for r in vqe})
        plt.boxplot(
            [
                [r["absolute_energy_error"] for r in vqe if r["variant"] == label]
                for label in labels
            ],
            tick_labels=labels,
        )
        plt.yscale("symlog", linthresh=1e-5)
        plt.ylabel("Absolute energy error (all sizes/seeds)")
        save("vqe-failure-study")
    noise = [r for r in rows if r["kind"] == "mitigation"]
    if noise:
        plt.figure(figsize=(8, 4))
        for method in ("linear", "richardson"):
            subset = [r for r in noise if r["extrapolation"] == method]
            plt.scatter(
                [r["shots"] for r in subset],
                [r["improvement"] for r in subset],
                label=method,
                alpha=0.35,
            )
        plt.axhline(0, color="black", linewidth=0.8)
        plt.xscale("log")
        plt.xlabel("Shots per term per scale")
        plt.ylabel("Raw error − mitigated error")
        plt.legend()
        save("mitigation-help-and-harm")
    scaling = [r for r in rows if r["kind"] == "scaling"]
    if scaling:
        plt.figure(figsize=(7, 4))
        for method in sorted({r["method"] for r in scaling}):
            subset = [r for r in scaling if r["method"] == method]
            plt.plot(
                [r["qubits"] for r in subset],
                [
                    r["reference_seconds"] if method == "exact" else r["method_seconds"]
                    for r in subset
                ],
                "o-",
                label=method,
            )
        plt.yscale("log")
        plt.xlabel("Qubits")
        plt.ylabel("Measured seconds (reference separate)")
        plt.legend()
        save("scaling-runtime")
    qaoa = [r for r in rows if r["kind"] == "qaoa"]
    if qaoa:
        plt.figure(figsize=(7, 4))
        for family in sorted({r["family"] for r in qaoa}):
            subset = [r for r in qaoa if r["family"] == family]
            plt.scatter(
                [r["depth"] for r in subset],
                [r["approximation_ratio"] for r in subset],
                label=family,
                alpha=0.5,
            )
        plt.xlabel("QAOA depth p")
        plt.ylabel("Expected cut / exact maximum")
        plt.legend()
        save("qaoa-graphs")
    discovery = [r for r in rows if r["kind"] == "discovery"]
    if discovery:
        plt.figure(figsize=(7, 4))
        for method in ("random", "evolutionary"):
            plt.scatter(
                [r[method]["gate_count"] for r in discovery],
                [r[method]["fidelity"] for r in discovery],
                label=method,
                alpha=0.5,
            )
        plt.xlabel("Gate count")
        plt.ylabel("Target-state fidelity")
        plt.legend()
        save("discovery-tradeoffs")
    chemistry = [r for r in rows if r["kind"] == "chemistry"]
    if chemistry:
        plt.figure(figsize=(7, 4))
        for metric in ("exact_energy", "energy", "hartree_fock_energy"):
            plt.scatter(
                [r["distance"] for r in chemistry], [r[metric] for r in chemistry], label=metric
            )
        plt.xlabel("H–H distance (bohr)")
        plt.ylabel("Total energy (Hartree)")
        plt.legend()
        save("h2-energy")
