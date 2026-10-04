# Contributing

Use a dedicated branch and Python 3.12. Install `[dev,ml,quantum,api]`. Run `ruff check .`, `ruff format --check .`, `mypy src/qas`, `pytest --cov=qas`, and `python -m build`. Add independent numerical expectations for scientific changes, not tests mirroring implementation. Keep CI credential-free and inexpensive; heavier benchmarks use the manual workflow.

Register hypotheses/criteria before execution. Persist negative and partial outcomes. Describe software capability separately from measurements and conclusions. Review the existing proprietary license before distributing; this repository is not currently licensed as open source.
