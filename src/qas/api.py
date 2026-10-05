"""Optional read-only artifact API; no experiment launch or credentials exposure."""

import json
from importlib.resources import files
from pathlib import Path


def create_app(root: str | Path = "results", registry: str = "experiments/registry.yaml"):
    import yaml
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import FileResponse, HTMLResponse

    from qas.registry import read

    app = FastAPI(title="QAS stored evidence")
    root = Path(root).resolve()

    def runs():
        return {
            p.parent.name: p
            for p in root.rglob("metrics.json")
            if p.resolve().is_relative_to(root) and (p.parent / "config.yaml").is_file()
        }

    def payload(file):
        try:
            return json.loads(file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise HTTPException(503, "Saved metrics temporarily unavailable") from exc

    @app.get("/", response_class=HTMLResponse)
    def dashboard():
        return files("qas").joinpath("dashboard.html").read_text(encoding="utf-8")

    @app.get("/run-catalog")
    def catalog():
        entries = []
        for run_id, file in runs().items():
            data = payload(file)
            config = yaml.safe_load((file.parent / "config.yaml").read_text(encoding="utf-8"))
            entries.append(
                {
                    "id": run_id,
                    "experiment_id": config.get("experiment_id", "unknown"),
                    "kind": config.get("kind", "tfim"),
                    "config": config,
                    "verdict": data.get("verdict", "BENCHMARKED"),
                    "records": len(data.get("rows", [data])),
                    "path": file.parent.relative_to(root).as_posix(),
                }
            )
        return sorted(entries, key=lambda item: item["id"], reverse=True)

    @app.get("/runs/{run_id}/figures")
    def figures(run_id: str):
        file = runs().get(run_id)
        if file is None:
            raise HTTPException(404, "Unknown run")
        return sorted(
            p.name
            for p in (file.parent / "figures").glob("*.png")
            if p.resolve().is_relative_to(root)
        )

    @app.get("/runs/{run_id}/figures/{filename}")
    def figure(run_id: str, filename: str):
        file = runs().get(run_id)
        if file is None or Path(filename).name != filename or not filename.endswith(".png"):
            raise HTTPException(404, "Unknown figure")
        image = (file.parent / "figures" / filename).resolve()
        if not image.is_relative_to(root) or not image.is_file():
            raise HTTPException(404, "Unknown figure")
        return FileResponse(image, media_type="image/png")

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
        return payload(file)

    @app.get("/results/summary")
    def summary():
        return {key: payload(file).get("seed_statistics", []) for key, file in runs().items()}

    return app
