# Hardware

`qas.hardware.Simulator(seed=0)` executes restricted circuits and returns reproducible sampled counts with shots/backend metadata. No credentials are needed. `IBMBackend(name, enabled=True)` requires optional `[hardware]` dependencies and a previously saved IBM account. It exposes submit, status and result methods using Runtime SamplerV2 and backend transpilation.

Live SDK and hardware behavior: NOT EXECUTED. No credentials/backend have been configured for this task. The opt-in denial is tested; the adapter remains PARTIAL pending SDK mock and service validation. Errors never print tokens. Existing user IBM account storage is used; secrets must never be committed. No actual QPU result is present.
