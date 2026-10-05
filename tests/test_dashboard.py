import json

import pytest
from fastapi.testclient import TestClient

from qas.api import create_app


def test_dashboard_catalog_and_figures(tmp_path):
    run = tmp_path / "runs" / "experiment" / "run-id"
    run.mkdir(parents=True)
    (run / "config.yaml").write_text("experiment_id: experiment\nqubits: [2]\nseeds: [0]")
    (run / "metrics.json").write_text(
        json.dumps({"rows": [{"method": "exact"}], "verdict": "INCONCLUSIVE"})
    )
    (run / "figures").mkdir()
    # PNG magic is sufficient for the HTTP transport test; actual plot rendering is tested separately.
    image = b"\x89PNG\r\n\x1a\n"
    (run / "figures" / "result.png").write_bytes(image)
    client = TestClient(create_app(tmp_path))
    page = client.get("/")
    assert page.status_code == 200 and "Evidence explorer" in page.text
    catalog = client.get("/run-catalog").json()
    assert catalog[0]["experiment_id"] == "experiment"
    assert catalog[0]["verdict"] == "INCONCLUSIVE"
    assert catalog[0]["records"] == 1
    assert client.get("/runs/run-id/figures").json() == ["result.png"]
    response = client.get("/runs/run-id/figures/result.png")
    assert response.content == image and response.headers["content-type"] == "image/png"
    assert client.get("/runs/run-id/figures/secret.env").status_code == 404
    assert client.get("/runs/unknown/figures").status_code == 404


def test_empty_dashboard(tmp_path):
    client = TestClient(create_app(tmp_path))
    assert client.get("/run-catalog").json() == []
    assert client.get("/runs").json() == []


@pytest.mark.parametrize("contents", ["{", "null", "[]", '{"rows": null}', '{"rows": [1]}'])
def test_invalid_saved_metrics_have_controlled_error(tmp_path, contents):
    run = tmp_path / "run-id"
    run.mkdir()
    (run / "config.yaml").write_text("experiment_id: test")
    metrics = run / "metrics.json"
    metrics.write_text(contents)
    client = TestClient(create_app(tmp_path))
    for endpoint in ("/run-catalog", "/runs/run-id", "/results/summary"):
        response = client.get(endpoint)
        assert response.status_code == 503
        assert response.json() == {"detail": "Saved metrics temporarily unavailable"}
    # An interrupted write can recover without restarting the API.
    metrics.write_text('{"rows": [], "verdict": "INCONCLUSIVE"}')
    assert client.get("/run-catalog").status_code == 200


@pytest.mark.parametrize("contents", ["[", "", "[]", "a scalar"])
def test_invalid_saved_config_has_controlled_error(tmp_path, contents):
    run = tmp_path / "run-id"
    run.mkdir()
    (run / "metrics.json").write_text('{"rows": []}')
    (run / "config.yaml").write_text(contents)
    client = TestClient(create_app(tmp_path))
    response = client.get("/run-catalog")
    assert response.status_code == 503
    assert response.json() == {"detail": "Saved configuration temporarily unavailable"}


def test_duplicate_run_ids_are_not_silently_overwritten(tmp_path):
    for experiment in ("first", "second"):
        run = tmp_path / experiment / "same-id"
        run.mkdir(parents=True)
        (run / "config.yaml").write_text(f"experiment_id: {experiment}")
        (run / "metrics.json").write_text('{"rows": []}')
    client = TestClient(create_app(tmp_path))
    for endpoint in ("/run-catalog", "/runs", "/runs/same-id", "/results/summary"):
        response = client.get(endpoint)
        assert response.status_code == 409
        assert response.json() == {"detail": "Duplicate run IDs in results root"}


@pytest.mark.parametrize(
    "contents", ['{"rows": [], "energy": NaN}', '{"rows": [], "energy": Infinity}']
)
def test_nonfinite_metrics_rejected(tmp_path, contents):
    run = tmp_path / "run"
    run.mkdir()
    (run / "config.yaml").write_text("experiment_id: test")
    (run / "metrics.json").write_text(contents)
    assert TestClient(create_app(tmp_path)).get("/run-catalog").status_code == 503


def test_missing_config_and_large_catalog(tmp_path):
    for i in range(60):
        run = tmp_path / f"run-{i:03}"
        run.mkdir()
        (run / "config.yaml").write_text("experiment_id: test")
        (run / "metrics.json").write_text('{"rows": []}')
    client = TestClient(create_app(tmp_path))
    assert len(client.get("/run-catalog?limit=10&offset=20").json()) == 10
    assert client.get("/run-catalog?limit=0").status_code == 422
    assert client.get("/run-catalog?offset=-1").status_code == 422
    (tmp_path / "run-000" / "config.yaml").unlink()
    assert client.get("/run-catalog").status_code == 503


def test_api_integrity_and_traversal(tmp_path):
    from qas.integrity import seal

    run = tmp_path / "run"
    run.mkdir()
    (run / "config.yaml").write_text("experiment_id: test")
    (run / "metrics.json").write_text('{"rows": []}')
    client = TestClient(create_app(tmp_path))
    assert client.get("/runs/run/integrity").json()["status"] == "UNSEALED"
    seal(run)
    assert client.get("/runs/run/integrity").json()["status"] == "VERIFIED"
    for path in (
        "/runs/run/figures/%2e%2e%2fconfig.yaml",
        "/runs/run/figures/C:%5csecret.png",
        "/runs/missing/integrity",
    ):
        assert client.get(path).status_code == 404
    (run / "metrics.json").write_text('{"rows": [{}]}')
    assert client.get("/runs/run/integrity").status_code == 409
