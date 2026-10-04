import json

import numpy as np
import pytest

from qas import artifacts, discovery, hardware, registry
from qas.benchmarks.tfim_compare import run
from qas.cli import main
from qas.config import Config, load


@pytest.mark.parametrize(
    "overrides",
    [
        {"qubits": [1]},
        {"seeds": [0, 0]},
        {"nqs_steps": 0},
        {"nqs_lr": -1},
        {"boundary": "bad"},
        {"experiment_id": "../../escape"},
        {"fidelity_min": 2},
        {"j": float("nan")},
    ],
)
def test_invalid_configuration(overrides):
    with pytest.raises(ValueError):
        Config(**overrides)


def test_safe_yaml(tmp_path):
    file = tmp_path / "bad.yaml"
    file.write_text("unknown: true")
    with pytest.raises(ValueError):
        load(file)


def test_discovery_and_simulator():
    bell = [discovery.Gate("H", 0), discovery.Gate("CNOT", 0, 1)]
    state = discovery.execute(bell, 2)
    assert np.allclose(state, [1 / np.sqrt(2), 0, 0, 1 / np.sqrt(2)])
    assert discovery.depth(bell, 2) == 2
    result = discovery.search(state, 2, budget=40)
    assert result == discovery.search(state, 2, budget=40)
    assert result["random"]["evaluations"] == result["evolutionary"]["evaluations"] == 40
    sim = hardware.Simulator()
    counts = sim.submit(bell, 2)["counts"]
    assert sum(counts.values()) == 1024
    assert set(counts) <= {"00", "11"}
    with pytest.raises(hardware.HardwareUnavailable):
        hardware.IBMBackend("unavailable")


def test_registry():
    entries = registry.read()
    assert entries[0]["id"] == "tfim-phase1"


def test_benchmark_artifacts_plot_summary_api(tmp_path):
    from qas.plotting import plot, summarize

    config = Config(qubits=(2,), seeds=(0, 1), nqs_steps=80, vqe_iterations=50)
    directory = run(config, tmp_path)
    payload = json.loads((directory / "metrics.json").read_text())
    assert len(payload["rows"]) == 5
    assert payload["complete"]
    assert payload["verdict"] in ("SUPPORTED", "NOT_SUPPORTED")
    for file in (
        "config.yaml",
        "environment.json",
        "metrics.json",
        "summary.csv",
        "stdout.log",
        "verdict.md",
    ):
        assert (directory / file).is_file()
    assert len(plot(directory)) == 16
    for checkpoint in (directory / "checkpoints").glob("nqs*.npz"):
        assert np.linalg.norm(np.load(checkpoint)["state"]) == pytest.approx(1)
    assert summarize(tmp_path, tmp_path / "table.csv").is_file()
    from fastapi.testclient import TestClient

    from qas.api import create_app

    client = TestClient(create_app(tmp_path))
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/runs/unknown").status_code == 404
    assert client.get(f"/runs/{directory.name}").json()["complete"]


def test_partial_verdict(tmp_path):
    config = Config(qubits=(2,), seeds=(0,))
    directory = run(config, tmp_path, ("exact",))
    assert json.loads((directory / "metrics.json").read_text())["verdict"] == "INCONCLUSIVE"


def test_cli(tmp_path):
    assert main(["experiment", "list"]) == 0
    assert main(["exact", "--config", "missing.yaml"]) == 2
    for command in ("noise", "mitigate", "qaoa", "discover"):
        args = [command, "--output", str(tmp_path)]
        if command in ("qaoa", "discover"):
            args += ["--budget", "20"]
        assert main(args) == 0


def test_failed_accuracy_retained(tmp_path):
    config = Config(qubits=(2,), seeds=(0,), energy_error_max=0)
    rows = [
        {"method": m, "qubits": 2, "absolute_energy_error": e, "fidelity": 1, "runtime_seconds": 0}
        for m, e in [("exact", 0), ("nqs", 1), ("vqe", 1)]
    ]
    for row in rows:
        row["seed"] = None if row["method"] == "exact" else 0
    artifacts.write_results(tmp_path, rows, config.dict())
    assert json.loads((tmp_path / "metrics.json").read_text())["verdict"] == "NOT_SUPPORTED"
