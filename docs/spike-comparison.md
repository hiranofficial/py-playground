# Spike comparison

Use this document to compare independent serving spikes on the same dimensions. Record measured evidence and test conditions rather than relying on qualitative labels. A local spike result is not production or model-risk approval.

## Evaluation dimensions

| Dimension | Evidence to capture |
| --- | --- |
| Cost | Build and runtime assumptions; estimated idle and load cost by environment; artifact storage and observability costs. |
| Latency | Warm and cold-start p50/p95/p99 latency, batch size, concurrency, payload shape, region, and test duration. |
| Throughput | Sustained requests and predictions per second at stated concurrency, plus the saturation point and limiting resource. |
| Reliability | Startup/readiness behavior, error rate under load, timeout/retry behavior, graceful shutdown, rollback path, and failure-test results. |
| Security and governance | Artifact format and integrity, dependency/image scans, identity and access model, secrets/data handling, signing/attestation, lineage, approvals, and audit evidence. |
| Operational effort | Local setup, build/deploy steps, configuration, monitoring and alerting, on-call/rollback complexity, and required platform skills. |
| Model-quality evidence | Dataset and split, metric definitions and thresholds, reproducibility, source-to-served-model parity, bias/limitations, version, and approval status. |

Use equivalent model inputs, load profiles, environments, and measurement methods wherever possible. Note unavoidable differences beside each result.

## 01 — FastAPI online inference

[Spike guide](../spikes/01-fastapi-online-inference/README.md) · [reusable spike framework](spike-framework.md)

| Dimension | Current evidence | Gap before comparison |
| --- | --- | --- |
| Cost | Minimal non-root Python container; no cloud resources provisioned. | Estimate Artifact Registry and Cloud Run costs under a stated traffic profile. |
| Latency | Each prediction response and structured log includes inference latency. | Run repeatable warm/cold p50/p95/p99 benchmarks. |
| Throughput | Batch contract supports 1–100 instances. | Measure sustained throughput and saturation under concurrency. |
| Reliability | Health/readiness endpoints, startup self-test, validation errors, and automated endpoint tests. | Exercise load, shutdown, missing/malformed package, timeout, and rollback scenarios. |
| Security and governance | ONNX instead of pickle, separate manifest, SHA-256 verification, pinned dependencies, non-root container, and route-to-live control guidance. | Run scans and demonstrate digest pinning, signing/attestation, access controls, and retained approvals. |
| Operational effort | Exact local, test, and Compose commands are documented; model package is self-contained. | Measure build/deploy time and create Cloud Run monitoring and rollback runbooks. |
| Model-quality evidence | Genuine logistic regression on the built-in Iris data; served class probabilities are tested. | Add a fixed evaluation split/CV, acceptance metrics, and scikit-learn-to-ONNX parity evidence. |

## Future spikes

- **02 — To be defined:** add only when an alternative serving approach and its hypothesis are agreed.
- **03 — To be defined:** reserve for a materially different approach; do not scaffold implementation in advance.
