# Scientific methodology

The original TFIM criteria and evidence are locked. The expanded suite is exploratory with a committed job plan. Energy/fidelity criteria are used as descriptive success rates, not evidence of computational advantage. Matrices use Pauli coefficients and big-endian wire ordering; exact TFIM/Heisenberg results are checked against QuTiP.

Complex autoregressive NQS uses causal Bernoulli probabilities and conditional phases, direct ancestral sampling, exact normalization and enumerated variational energy. Adam/SGD support float64 parameters, complex128 states, gradient histories, early stopping and full optimizer resume. No mixed-precision or scalable VMC claim is made.

VQE studies isolate depth, initialization, budget, restart and optimizer changes against the unchanged depth-3 RY baseline; the ZZ/RX problem ansatz is a separate variant. Gradients, termination reasons, all restart attempts and final states are retained. QAOA exact enumeration references several graph families; final sampling is distinct from analytic optimization and different optimizer budget semantics are recorded.

Circuit noise applies local channels after each gate. Finite shots independently measure Pauli terms from density-matrix Born probabilities; estimator variance is propagated with independent terms. Measurement rotations are ideal. Local unitary folding uses odd scales 1,3,5; linear and Richardson fits retain signed weights and unbounded estimates. Report all negative improvements, total shots and equal-total-shot raw comparisons. These measurements are distinct from historical analytic probability-scaling cancellation and from unexecuted hardware noise.

Search methods use equal fitness evaluations, configurable vocabulary/population, crossover/mutation/elitism and nondominated archives. Human baselines are separate fixed circuits. Projector energy objectives are not claimed to be physical local Hamiltonians. H2 uses STO-3G, bohr, Hartree total energies, Jordan–Wigner, two electrons in four spin orbitals and a double-excitation ansatz.

Mean, sample SD, median, extrema and success rates describe stochastic outcomes. Approximate Student-t mean intervals require at least five seeds and independence/normality assumptions; they do not quantify exact-reference uncertainty. No significance tests are reported. Runtime and sampled-process-RSS scope, cold imports, checkpoint I/O, one-machine sampling and separate reference costs limit comparisons.

References: [PennyLane chemistry](https://docs.pennylane.ai/en/stable/introduction/chemistry.html), [digital ZNE](https://arxiv.org/abs/2005.10921), [Mitiq folding](https://mitiq.readthedocs.io/en/stable/examples/scaling.html).
