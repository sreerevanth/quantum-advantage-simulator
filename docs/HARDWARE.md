# Hardware

`qas.hardware.Simulator(seed=0)` executes restricted circuits and returns reproducible sampled counts with shots/backend metadata. No credentials are needed. `IBMBackend(name, enabled=True)` requires optional `[hardware]` dependencies and a previously saved IBM account. It exposes submit, status and result methods using Runtime SamplerV2 and backend transpilation.

Live SDK and hardware behavior: NOT EXECUTED. No credentials/backend have been configured for this task. Opt-in denial and mocked submission/transpilation/status/result paths are tested. Errors never print tokens. Existing saved IBM credentials are used; secrets must never be committed. No actual QPU result is present. The API follows the [IBM Sampler quickstart](https://quantum.cloud.ibm.com/docs/en/guides/get-started-with-sampler); live SDK compatibility requires provider validation.
