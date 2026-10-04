"""Optional read-only artifact API; no experiment launch or credentials exposure."""

import json
from pathlib import Path


def create_app(root: str | Path = "results/runs", registry: str = "experiments/registry.yaml"):
    from fastapi import FastAPI, HTTPException

    from qas.registry import read

    app = FastAPI(title="QAS stored evidence")
    root = Path(root).resolve()

    def runs():
        return {p.parent.name: p for p in root.glob("*/*/metrics.json")}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/experiments")
    def experiments():
        return read(registry)

    @app.get("/experiments/{experiment_id}")
    def experiment(experiment_id: str):
        for entry in read(registry):
            if entry["id"] == experiment_id:
                return entry
        raise HTTPException(404, "Unknown experiment")

    @app.get("/runs")
    def list_runs():
        return list(runs())

    @app.get("/runs/{run_id}")
    def get_run(run_id: str):
        file = runs().get(run_id)
        if file is None:
            raise HTTPException(404, "Unknown run")
        return json.loads(file.read_text())

    @app.get("/results/summary")
    def summary():
        return {
            key: json.loads(file.read_text()).get("seed_statistics", [])
            for key, file in runs().items()
        }

    return app
