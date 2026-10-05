# Experiments

`qas suite --quick` runs 21 integration jobs. `qas suite --full --device cpu --seed 0` runs the committed 569-job practical study. `--output DIRECTORY` changes the artifact root. `--resume RUN` requires identical mode, seed and resolved device. The frozen plan is copied to each run; stored configuration mismatches and corruption fail visibly.

Full study: 45 NQS jobs across three models/three sizes/five seeds; 105 VQE jobs across seven variants/three sizes/five seeds; 240 mitigation jobs across two sizes/four strengths/three shot counts/two extrapolators/five seeds; 120 QAOA jobs across four graph families/three depths/two optimizers/five seeds; 30 search jobs across three targets/two objectives/five seeds; 15 H2 jobs across three geometries/five seeds; 14 scaling jobs. See `experiments/configs/research_full.yaml` and `experiments/research_registry.yaml` for actual parameters.

The original `qas benchmark --config experiments/configs/tfim_phase1.yaml` remains available. Its registry is `experiments/registry.yaml`; the new suite's descriptive protocol is separate. Original analytic labs retain their commands (`noise`, `mitigate`, `qaoa`, `discover`). New measurements never replace historical directories.

CLI help documents exact, nqs, vqe, benchmark, suite, noise, mitigate, qaoa, discover, experiment, results, verify, hardware, doctor and validate. `qas hardware --backend BACKEND --shots 1000 --job-id ID` retrieves an existing hardware job without resubmitting it.
