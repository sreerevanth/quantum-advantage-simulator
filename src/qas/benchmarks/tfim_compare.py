"""Execute the locked small-system comparison."""

import argparse
import logging
import time
import tracemalloc
from pathlib import Path

import numpy as np

from qas import artifacts, exact, metrics, nqs, variational
from qas.config import Config, load


def run(
    config: Config, root: str | Path = "results/runs", methods: tuple = ("exact", "nqs", "vqe")
) -> Path:
    directory = artifacts.create(root, config.dict())
    logger = logging.getLogger(str(directory))
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(directory / "stdout.log", encoding="utf-8")
    logger.addHandler(handler)
    rows = []
    try:
        for n in config.qubits:
            tracemalloc.start()
            start = time.perf_counter()
            ham = exact.hamiltonian(n, config.j, config.h, config.boundary)
            eigenvalues, eigenvectors = exact.solve(ham)
            reference = eigenvectors[:, 0]
            elapsed = time.perf_counter() - start
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            rows.append(
                {
                    "method": "exact",
                    "qubits": n,
                    "seed": None,
                    **metrics.compare(reference, reference, ham, n),
                    "runtime_seconds": elapsed,
                    "python_peak_bytes": peak,
                    "ground_gap": float(eigenvalues[1] - eigenvalues[0]),
                    "history": [],
                }
            )
            np.savez_compressed(directory / "checkpoints" / f"exact-{n}.npz", state=reference)
            for method in methods:
                if method == "exact":
                    continue
                for seed in config.seeds:
                    tracemalloc.start()
                    start = time.perf_counter()
                    if method == "nqs":
                        result = nqs.train(
                            ham,
                            n,
                            seed,
                            config.nqs_steps,
                            config.nqs_lr,
                            config.nqs_hidden,
                            config.tolerance,
                        )
                    elif method == "vqe":
                        result = variational.vqe(
                            ham,
                            n,
                            seed,
                            config.vqe_depth,
                            config.vqe_iterations,
                            config.tolerance,
                            config.vqe_ansatz,
                            config.vqe_optimizer,
                        )
                    else:
                        raise ValueError(f"Unknown method {method}")
                    elapsed = time.perf_counter() - start
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    row = {
                        "method": method,
                        "qubits": n,
                        "seed": seed,
                        **metrics.compare(result.pop("state"), reference, ham, n),
                        "runtime_seconds": elapsed,
                        "python_peak_bytes": peak,
                    }
                    parameters = result.pop("parameters")
                    np.savez_compressed(
                        directory / "checkpoints" / f"{method}-{n}-{seed}.npz", **parameters
                    )
                    row.update(result)
                    rows.append(row)
                    logger.info(
                        "%s n=%d seed=%d energy_error=%g",
                        method,
                        n,
                        seed,
                        row["absolute_energy_error"],
                    )
                    print(
                        f"{method} n={n} seed={seed} error={row['absolute_energy_error']:.6g}",
                        flush=True,
                    )
                    artifacts.write_results(directory, rows, config.dict())
        artifacts.write_results(directory, rows, config.dict())
    except Exception:
        logger.exception("Run failed")
        if rows:
            artifacts.write_results(directory, rows, config.dict())
        raise
    finally:
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        handler.close()
        logger.removeHandler(handler)
    return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", default="results/runs")
    args = parser.parse_args()
    print(run(load(args.config), args.output))


if __name__ == "__main__":
    main()
