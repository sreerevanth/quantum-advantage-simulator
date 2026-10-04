"""Run release checks and persist exact return codes/output for review."""

import json
import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
output = root / "results" / "validation"
output.mkdir(parents=True, exist_ok=True)
commands = {
    "lint": [sys.executable, "-m", "ruff", "check", "."],
    "format": [sys.executable, "-m", "ruff", "format", "--check", "."],
    "types": [sys.executable, "-m", "mypy", "src/qas"],
    "tests": [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "--cov=qas",
        "--cov-report=term-missing",
        "--cov-report=json:results/validation/coverage.json",
    ],
    "dependencies": [sys.executable, "-m", "pip", "check"],
    "build": [sys.executable, "-m", "build"],
    "cli": [sys.executable, "-m", "qas.cli", "--help"],
}
env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
results = {}
for name, command in commands.items():
    result = subprocess.run(
        command,
        cwd=root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        errors="replace",
    )
    (output / f"{name}.log").write_text(result.stdout, encoding="utf-8")
    results[name] = {"command": command, "returncode": result.returncode}
    print(f"{name}: {result.returncode}", flush=True)
(output / "checks.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
sys.exit(int(any(r["returncode"] != 0 for r in results.values())))
