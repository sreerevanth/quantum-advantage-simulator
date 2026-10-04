# Experiments

From the repository root:

```sh
qas experiment list
qas experiment inspect tfim-phase1
qas benchmark --config experiments/configs/tfim_smoke.yaml
python -m qas.benchmarks.tfim_compare --config experiments/configs/tfim_phase1.yaml
qas exact --config experiments/configs/tfim_smoke.yaml
qas nqs --config experiments/configs/tfim_smoke.yaml
qas vqe --config experiments/configs/tfim_smoke.yaml
qas noise --probability 0.05
qas mitigate --probability 0.05 --scales 1 2 3
qas qaoa --qubits 3 --seed 0 --budget 100
qas discover --qubits 2 --seed 0 --budget 200
qas results summarize results/runs --output results/tables/combined.csv
qas results plot results/runs/EXPERIMENT/RUN
```

`experiments/registry.yaml` records the locked Phase-1 experiment. Config validation rejects unknown keys, duplicate seeds, unsafe IDs, invalid finite values and unsupported sizes. Registry validation checks required fields, paths, IDs, seeds, and accuracy criteria against the config. Exploratory labs remain separate. Each accepts `--config experiments/configs/NAME.yaml`: noise_sweep, zne, qaoa, discovery. Configs lock channel/scales, graph/depth, or search budgets and seeds.
