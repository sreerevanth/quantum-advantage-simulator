import json

import pytest

from qas import labs


@pytest.mark.parametrize("file", ["noise_sweep", "zne", "qaoa", "discovery"])
def test_lab_configuration(file):
    assert labs.load(f"experiments/configs/{file}.yaml")["qubits"] >= 2


def test_lab_artifacts(tmp_path):
    config = labs.load("experiments/configs/zne.yaml")
    directory = labs.run(config, tmp_path)
    payload = json.loads((directory / "metrics.json").read_text())
    assert payload["verdict"] == "SUPPORTED"
    assert len(payload["rows"]) == 5
    assert (directory / "figures/noise_errors.png").is_file()


@pytest.mark.parametrize(
    "content",
    ["kind: invalid", "kind: qaoa\nqubits: 100", "kind: noise\nqubits: 2\nscales: [0, 1]"],
)
def test_bad_lab_config(tmp_path, content):
    file = tmp_path / "bad.yaml"
    file.write_text(content)
    with pytest.raises(ValueError):
        labs.load(file)
