# Contributing

Use a dedicated branch. Install `.[dev,ml,quantum,api,validation]` on Python 3.11–3.13. Run `python scripts/validate_release.py`. Add independent scientific expectations and regression cases; never relax assertions to fit measured outcomes. Keep full experiments out of PR CI and use the manual research workflow.

Preserve historical evidence. Commit new plans before experiments, keep all negative/partial results and record source/environment/configuration. Never alter completed sealed artifacts. Generate reports from measured artifacts only. Contributions are under Apache-2.0; dependencies retain their licenses. See docs/METHODOLOGY.md and docs/REPRODUCIBILITY.md.
