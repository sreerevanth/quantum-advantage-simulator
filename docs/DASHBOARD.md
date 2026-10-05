# Saved-evidence dashboard

Install the optional API dependencies with `pip install -e ".[api]"` from the checkout, then run:

```powershell
python -m uvicorn qas.api:create_app --factory --host 127.0.0.1 --port 8765
```

Open http://127.0.0.1:8765. The default results root is `results` relative to the working directory. Run selection displays recorded verdicts, metric rows, configuration, seed statistics and persisted PNG figures. TFIM, analytic noise, QAOA and circuit-search artifacts are supported; the human circuit baseline appears separately from equal-budget searches.

The API and dashboard are read-only. They do not train models, submit hardware jobs, or recalculate research verdicts. File serving is restricted to PNG artifacts inside discovered run directories and the configured results root. The default launch binds only to the local computer. An empty catalog is valid when no saved artifacts exist.

Malformed or temporarily incomplete saved metrics/configurations return HTTP 503 with a specific error message. Duplicate run directory names return HTTP 409 rather than silently selecting one run; give each run a unique directory name. Configurations resolving outside the results root are excluded from discovery. Repaired files are read on the next request without restarting the service.
