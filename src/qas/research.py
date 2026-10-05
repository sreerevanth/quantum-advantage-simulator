"""One-command, resumable practical research suite with immutable completed evidence."""

import csv
import hashlib
import json
import time
from functools import lru_cache
from pathlib import Path

import numpy as np
import yaml

from qas import artifacts, exact, metrics
from qas.integrity import atomic_json, digest, seal, verify
from qas.resources import MemorySampler


@lru_cache(maxsize=20)
def reference(n, model="tfim"):
    matrix = exact.hamiltonian(
        n,
        model="heisenberg" if model == "heisenberg" else "tfim",
        h=0 if model == "heisenberg" else 1,
    )
    if model == "complex":
        matrix = matrix + 0.4 * exact.operator(n, {0: "Y"})
    return matrix, exact.solve(matrix)[1][:, 0]


def plan(full=False, seed=0, device="cpu"):
    seeds = list(range(seed, seed + (5 if full else 1)))
    jobs = []

    def add(kind, **kwargs):
        jobs.append(dict(kind=kind, **kwargs))

    for n in [2, 4, 6] if full else [2]:
        for model in ("tfim", "heisenberg", "complex"):
            for s in seeds:
                add(
                    "nqs",
                    qubits=n,
                    model=model,
                    seed=s,
                    steps=350 if full else 80,
                    hidden=16,
                    optimizer="Adam",
                    device=device,
                )
    for n in [6, 7, 8] if full else [2]:
        variants = [
            ("locked", "ry", 3, "normal", "BFGS", 150, 1),
            ("depth", "ry", 6, "normal", "BFGS", 150, 1),
            ("initialization", "ry", 3, "uniform", "BFGS", 150, 1),
            ("budget", "ry", 3, "normal", "BFGS", 300, 1),
            ("problem", "tfim", 4, "normal", "BFGS", 150, 1),
            ("restart", "ry", 3, "normal", "BFGS", 150, 2),
            ("optimizer", "ry", 3, "normal", "L-BFGS-B", 150, 1),
        ]
        for variant, ansatz, depth, init, opt, budget, restarts in (
            variants if full else variants[:1] + variants[4:5]
        ):
            for s in seeds:
                add(
                    "vqe",
                    qubits=n,
                    seed=s,
                    variant=variant,
                    ansatz=ansatz,
                    depth=depth,
                    initialization=init,
                    optimizer=opt,
                    iterations=budget if full else 40,
                    restarts=restarts,
                )
    for n in [2, 3] if full else [2]:
        for probability in [0.0, 0.002, 0.02, 0.1] if full else [0.02]:
            for shots in [100, 1000, 10000] if full else [100]:
                for method in ("linear", "richardson"):
                    for s in seeds:
                        add(
                            "mitigation",
                            qubits=n,
                            seed=s,
                            probability=probability,
                            shots=shots,
                            extrapolation=method,
                            allocation="equal",
                        )
    for family in ("path", "cycle", "random", "dense"):
        for depth in [1, 2, 3] if full else [1]:
            for optimizer in ["BFGS", "COBYLA"] if full else ["BFGS"]:
                for s in seeds:
                    add(
                        "qaoa",
                        qubits=5 if full else 3,
                        seed=s,
                        family=family,
                        depth=depth,
                        optimizer=optimizer,
                        iterations=100 if full else 30,
                        shots=1000,
                    )
    for target in ("bell", "ghz", "cluster"):
        for objective in ["fidelity", "energy"] if full else ["fidelity"]:
            for s in seeds:
                add(
                    "discovery",
                    qubits=2 if target == "bell" else 3,
                    seed=s,
                    target=target,
                    objective=objective,
                    budget=300 if full else 40,
                )
    for distance in [1.0, 1.4, 2.0] if full else [1.4]:
        for s in seeds:
            add("chemistry", qubits=4, seed=s, distance=distance)
    for n in [2, 4, 6, 8, 10] if full else [2, 4]:
        for method in ("exact", "autoregressive", "vqe"):
            if n > 8 and method == "vqe":
                continue
            add(
                "scaling",
                qubits=n,
                seed=seed,
                method=method,
                steps=150 if full else 30,
                device=device,
            )
    return jobs


def evaluate(job, checkpoints):
    from qas import autoregressive, variational

    n = job["qubits"]
    seed = job["seed"]
    kind = job["kind"]
    if kind == "nqs":
        matrix, ground = reference(n, job["model"])
        path = checkpoints / "model.pt"
        result = autoregressive.train(
            matrix,
            n,
            seed,
            job["steps"],
            hidden=job["hidden"],
            optimizer=job["optimizer"],
            device=job["device"],
            checkpoint=path,
            resume=path.exists(),
        )
        np.savez_compressed(checkpoints / "state.npz", state=result["state"])
        return {
            **metrics.compare(result["state"], ground, matrix, n),
            **{k: v for k, v in result.items() if k not in ("state", "model")},
        }
    if kind == "vqe":
        matrix, ground = reference(n)
        attempts = []
        for restart in range(job["restarts"]):
            path = checkpoints / f"restart-{restart}.json"
            statepath = checkpoints / f"restart-{restart}.npz"
            if path.exists() and statepath.exists():
                result = json.loads(path.read_text())
                state = np.load(statepath)["state"]
            else:
                result = variational.vqe(
                    matrix,
                    n,
                    seed + restart * 7919,
                    job["depth"],
                    job["iterations"],
                    ansatz=job["ansatz"],
                    optimizer=job["optimizer"],
                    initialization=job["initialization"],
                )
                state = result.pop("state")
                parameters = result.pop("parameters")
                np.savez_compressed(statepath, state=state, weights=parameters["weights"])
                atomic_json(path, result)
            attempts.append({**metrics.compare(state, ground, matrix, n), **result})
        best = min(attempts, key=lambda r: r["energy"])
        return {
            **best,
            "attempts": attempts,
            "total_iterations": sum(r["iterations"] for r in attempts),
            "success": best["absolute_energy_error"] <= 0.05 and best["fidelity"] >= 0.95,
        }
    if kind == "mitigation":
        from qas.shot_noise import Operation, tfim_terms, zne

        circuit = [Operation("RY", (i,), 0.7 + 0.1 * i) for i in range(n)] + [
            Operation("CNOT", (i, i + 1)) for i in range(n - 1)
        ]
        p = job["probability"]
        noise = dict(
            depolarizing=p,
            amplitude_damping=p / 2,
            phase_damping=p / 3,
            readout=p / 4,
            two_qubit_multiplier=2,
        )
        return {
            **zne(
                circuit,
                n,
                tfim_terms(n),
                noise,
                job["shots"],
                seed,
                method=job["extrapolation"],
                allocation=job["allocation"],
            ),
            "noise": noise,
        }
    if kind == "qaoa":
        edges = [[i, i + 1] for i in range(n - 1)]
        if job["family"] == "cycle":
            edges.append([0, n - 1])
        if job["family"] == "dense":
            edges = [[i, j] for i in range(n) for j in range(i + 1, n)]
        if job["family"] == "random":
            rng = np.random.default_rng(174)
            edges = [
                [i, j]
                for i in range(n)
                for j in range(i + 1, n)
                if j == i + 1 or rng.random() < 0.55
            ]
        return {
            **variational.qaoa(
                n, edges, seed, job["depth"], job["iterations"], job["optimizer"], job["shots"]
            ),
            "edges": edges,
        }
    if kind == "discovery":
        from qas.discovery import Gate, depth, execute
        from qas.search_lab import search

        human = [Gate("H", 0)] + [Gate("CNOT", i, i + 1) for i in range(n - 1)]
        if job["target"] == "cluster":
            human = [Gate("H", i) for i in range(n)]
            for i in range(n - 1):
                human.extend([Gate("H", i + 1), Gate("CNOT", i, i + 1), Gate("H", i + 1)])
        target = execute(human, n)
        ham = -np.outer(target, target.conj())
        path = checkpoints / "search.json"
        result = search(
            target,
            n,
            seed,
            job["budget"],
            objective=job["objective"],
            matrix=ham,
            checkpoint=path,
            resume=path.exists(),
        )
        return {
            **result,
            "human": dict(
                fidelity=1.0,
                energy=-1.0,
                gate_count=len(human),
                depth=depth(human, n),
                evaluations=1,
            ),
            "energy_objective": "negative target projector, not a local many-body Hamiltonian",
        }
    if kind == "chemistry":
        from qas.chemistry import h2

        return h2(job["distance"], seed)
    if kind == "scaling":
        # Reference preparation timed separately for approximate methods.
        start = time.perf_counter()
        matrix = exact.hamiltonian(n)
        ground = exact.solve(matrix)[1][:, 0]
        reference_seconds = time.perf_counter() - start
        start = time.perf_counter()
        if job["method"] == "exact":
            result = dict(state=ground, iterations=1, parameter_count=0)
        elif job["method"] == "autoregressive":
            result = autoregressive.train(
                matrix,
                n,
                seed,
                job["steps"],
                device=job["device"],
                checkpoint=checkpoints / "model.pt",
                resume=(checkpoints / "model.pt").exists(),
            )
        else:
            result = variational.vqe(matrix, n, seed, depth=3, iterations=job["steps"])
        return {
            **metrics.compare(result["state"], ground, matrix, n),
            "iterations": result["iterations"],
            "parameter_count": result.get("parameter_count", 0),
            "state_space_size": 2**n,
            "reference_seconds": reference_seconds,
            "method_seconds": time.perf_counter() - start,
            "hamiltonian_bytes": matrix.nbytes,
            "state_bytes": ground.nbytes,
        }
    raise ValueError("Unknown suite job")


def run(full=False, seed=0, device="cpu", output="results/research", resume=None):
    from qas.autoregressive import device_for

    device = str(device_for(device))
    jobs = plan(full, seed, device)
    config = dict(
        experiment_id="research-full" if full else "research-quick",
        kind="research-suite",
        full=full,
        seeds=list(range(seed, seed + (5 if full else 1))),
        device=device,
        jobs=jobs,
        criteria={"accuracy_energy_max": 0.05, "accuracy_fidelity_min": 0.95},
        limitations=[
            "Small classical simulations; no quantum advantage test",
            "Seed intervals are approximate",
            "Density noise is a simulator model, not calibrated hardware",
        ],
    )
    if resume:
        directory = Path(resume)
        if yaml.safe_load((directory / "config.yaml").read_text()) != config:
            raise ValueError("Resume configuration differs from recorded plan")
        if (directory / "manifest.json").exists():
            verify(directory)
            return directory
    else:
        directory = artifacts.create(output, config)
        atomic_json(directory / "plan.json", jobs)
    tasks = directory / "tasks"
    tasks.mkdir(exist_ok=True)
    rows = []
    for index, job in enumerate(jobs):
        key = hashlib.sha256(json.dumps(job, sort_keys=True).encode()).hexdigest()[:16]
        task = tasks / (key + ".json")
        checkpoints = directory / "checkpoints" / key
        checkpoints.mkdir(exist_ok=True)
        if task.exists():
            record = json.loads(task.read_text())
            if (
                record["job"] != job
                or record["sha256"]
                != hashlib.sha256(
                    json.dumps(record["row"], sort_keys=True, allow_nan=False).encode()
                ).hexdigest()
            ):
                raise ValueError("Corrupt completed task")
            for relative, checksum in record["checkpoints"].items():
                path = (directory / relative).resolve()
                if (
                    not path.is_relative_to(directory.resolve())
                    or not path.is_file()
                    or digest(path) != checksum
                ):
                    raise ValueError("Corrupt task checkpoint")
            row = record["row"]
        else:
            print(f"{index + 1}/{len(jobs)} {job}", flush=True)
            start = time.perf_counter()
            try:
                with MemorySampler() as memory:
                    result = evaluate(job, checkpoints)
                peak = memory.peak
            except Exception as exc:
                atomic_json(
                    directory / "failure.json",
                    dict(job=job, error_type=type(exc).__name__, message=str(exc)),
                )
                raise
            row = {
                **job,
                **result,
                "job_id": key,
                "wall_seconds": time.perf_counter() - start,
                "peak_memory_bytes": peak,
                "rss_start_bytes": memory.start,
                "memory_scope": "Process RSS sampled every 10ms; includes imported dependencies, may miss short peaks",
            }
            record = dict(
                job=job,
                row=row,
                sha256=hashlib.sha256(
                    json.dumps(row, sort_keys=True, allow_nan=False).encode()
                ).hexdigest(),
                checkpoints={
                    p.relative_to(directory).as_posix(): digest(p)
                    for p in checkpoints.rglob("*")
                    if p.is_file()
                },
            )
            atomic_json(task, record)
        rows.append(row)
        atomic_json(
            directory / "metrics.json",
            dict(
                rows=rows,
                complete=len(rows) == len(jobs),
                verdict="BENCHMARKED" if len(rows) == len(jobs) else "INCONCLUSIVE",
                expected_jobs=len(jobs),
                limitations=config["limitations"],
            ),
        )
    summarize(directory, rows)
    if (directory / "failure.json").exists():
        atomic_json(directory / "recovery.json", {"status": "Recovered; prior failure retained"})
    seal(directory)
    return directory


def summarize(directory, rows):
    from qas.statistical import describe

    grouped: dict[str, list[dict]] = {}
    for row in rows:
        key = json.dumps(
            {
                k: v
                for k, v in row.items()
                if k
                in (
                    "kind",
                    "qubits",
                    "model",
                    "variant",
                    "family",
                    "depth",
                    "optimizer",
                    "probability",
                    "shots",
                    "extrapolation",
                    "target",
                    "objective",
                    "distance",
                    "method",
                )
            },
            sort_keys=True,
        )
        grouped.setdefault(key, []).append(row)
    summary = []
    for key, selected in grouped.items():
        stats = {}
        for metric in (
            "absolute_energy_error",
            "fidelity",
            "raw_error",
            "mitigated_error",
            "equal_budget_raw_error",
            "approximation_ratio",
            "wall_seconds",
            "peak_memory_bytes",
        ):
            values = [r[metric] for r in selected if metric in r]
            if values:
                stats[metric] = describe(values)
        success = [r["success"] for r in selected if "success" in r]
        helped = [r["helped"] for r in selected if "helped" in r]
        summary.append(
            dict(
                group=json.loads(key),
                statistics=stats,
                success_rate=float(np.mean(success)) if success else None,
                mitigation_help_rate=float(np.mean(helped)) if helped else None,
            )
        )
    atomic_json(directory / "statistics.json", summary)
    payload = json.loads((directory / "metrics.json").read_text())
    payload["seed_statistics"] = summary
    atomic_json(directory / "metrics.json", payload)
    keys = sorted(
        {
            k
            for r in rows
            for k, v in r.items()
            if isinstance(v, (str, int, float, bool)) or v is None
        }
    )
    with (directory / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows([{k: v for k, v in r.items() if k in keys} for r in rows])
    from qas.research_plots import plot

    plot(directory, rows)
    (directory / "verdict.md").write_text(
        "# BENCHMARKED\n\nExploratory controlled comparisons. No general advantage established. All rows and negative outcomes retained.\n",
        encoding="utf-8",
    )
