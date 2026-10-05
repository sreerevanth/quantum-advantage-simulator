import json

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
