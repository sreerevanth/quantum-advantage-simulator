"""Validate preregistered experiments before dispatch."""

from pathlib import Path

import yaml

REQUIRED = {
    "id",
    "name",
    "description",
    "hypothesis",
    "baseline",
    "methods",
    "controlled_variables",
    "primary_metrics",
    "secondary_metrics",
    "criteria",
    "seeds",
    "resource_budget",
    "configuration",
    "expected_artifacts",
    "status",
}


def read(path: str | Path = "experiments/registry.yaml") -> list[dict]:
    path = Path(path)
    entries = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise ValueError("Registry must be a list")
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != REQUIRED:
            raise ValueError("Registry entry must contain exactly the required fields")
        for key in REQUIRED - {
            "methods",
            "controlled_variables",
            "primary_metrics",
            "secondary_metrics",
            "criteria",
            "seeds",
            "resource_budget",
            "expected_artifacts",
        }:
            if not isinstance(entry[key], str) or not entry[key].strip():
                raise ValueError(f"Registry field {key} must be nonempty text")
        for key in (
            "methods",
            "controlled_variables",
            "primary_metrics",
            "secondary_metrics",
            "expected_artifacts",
        ):
            if (
                not isinstance(entry[key], list)
                or not entry[key]
                or any(not isinstance(v, str) for v in entry[key])
            ):
                raise ValueError(f"Registry field {key} must be a nonempty text list")
        if not isinstance(entry["criteria"], dict) or not isinstance(
            entry["resource_budget"], dict
        ):
            raise ValueError("Criteria and budget must be mappings")
        if (
            not isinstance(entry["seeds"], list)
            or not entry["seeds"]
            or any(type(s) is not int or s < 0 for s in entry["seeds"])
        ):
            raise ValueError("Invalid seeds")
        if entry["id"] in seen:
            raise ValueError("Duplicate experiment ID")
        seen.add(entry["id"])
        resolved = (path.parent.parent / entry["configuration"]).resolve()
        if not resolved.is_relative_to(path.parent.parent.resolve()) or not resolved.is_file():
            raise ValueError("Unsafe or missing experiment configuration")
        from qas.config import load

        config = load(resolved)
        if entry["status"] not in {
            "IMPLEMENTED",
            "VALIDATED",
            "PARTIAL",
            "NOT IMPLEMENTED",
            "BLOCKED",
            "NOT EXECUTED",
        }:
            raise ValueError("Unknown implementation status")
        budget = {
            "qubits_max": max(config.qubits),
            "nqs_steps": config.nqs_steps,
            "vqe_iterations": config.vqe_iterations,
            "vqe_depth": config.vqe_depth,
        }
        if entry["resource_budget"] != budget or entry["methods"] != ["exact", "nqs", "vqe"]:
            raise ValueError("Registry budget or methods disagree with locked configuration")
        if config.experiment_id != entry["id"] or list(config.seeds) != entry["seeds"]:
            raise ValueError("Registry and configuration disagree")
        if entry["criteria"] != {
            "energy_error_max": config.energy_error_max,
            "fidelity_min": config.fidelity_min,
        }:
            raise ValueError("Registry criteria disagree with locked configuration")
    return entries
