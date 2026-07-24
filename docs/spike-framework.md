# Experiment spike framework

Use this framework to define, run, and conclude each independent spike. Keep the write-up short, link to reproducible evidence, and distinguish observed results from assumptions. A successful technical spike is not production or model-risk approval.

The same headings apply to online FastAPI services, Vertex AI batch pipelines, BigQuery ML, Workbench experiments, GKE batch workloads, and GenAI control-plane approaches. Mark prompts that do not apply as `N/A` with a reason.

## 1. Purpose and hypothesis

- **Decision to inform:** What concrete choice will this spike support, and who owns it?
- **Hypothesis:** State one falsifiable claim about the approach.
- **Scope:** Define the use case, users, workload shape, environment, and time box.
- **Alternatives:** Name the approaches being compared and the current baseline.
- **Exit criteria:** Link measurable pass/fail thresholds to the [spike comparison](spike-comparison.md).

## 2. Architecture and runtime

- Draw or describe components, execution flow, boundaries, dependencies, regions, and trust zones.
- Identify the runtime and control plane, including versions, compute shape, scaling/concurrency, scheduling, timeouts, retries, and failure handling.
- Define interfaces: synchronous API, batch inputs/outputs, SQL objects, notebook execution, job specification, or model/tool contract.
- Record configuration sources, identity, networking, persistence, observability, and teardown behavior.

## 3. Data and model or artifact

- Describe input/output schemas, validation, data source, classification, residency, retention, and any representative-data limitations.
- Identify the model, query, notebook, container, prompt, tool definition, or other executable artifact; record its version and owner.
- Capture training/build inputs, preprocessing, feature or prompt order, labels, runtime compatibility, lineage, integrity checksum/digest, and storage location as applicable.
- Explain how an artifact is promoted, reproduced, compared for parity, and rolled back without relying on a mutable name.

## 4. Run and test procedure

Provide exact commands or SQL/notebook/job steps from a clean checkout:

1. Prerequisites, authentication, project/region, permissions, dependencies, and expected cost-bearing resources.
2. Data preparation and artifact build or selection.
3. Local or managed execution, including configuration and a representative invocation.
4. Automated correctness, contract, failure, integrity, and security tests.
5. Load, scale, or batch-volume test with inputs, concurrency, duration, and measurement tooling.
6. Result and log locations, cleanup commands, and evidence-retention location.

Never place secrets, regulated data, credentials, or sensitive payloads in the repository or captured logs.

## 5. Success measures and evidence

Predeclare thresholds before measuring and record the environment and timestamp with every result.

| Dimension | Threshold | Observed result | Evidence |
| --- | --- | --- | --- |
| Correctness and contract | TBD | Not run | Link test output or query results. |
| Cost | TBD | Not measured | Link estimate and measured billing/resource data. |
| Latency | TBD | Not measured | Record warm/cold p50/p95/p99 or batch duration. |
| Throughput and scale | TBD | Not measured | Record sustained volume, concurrency, and saturation. |
| Reliability | TBD | Not tested | Record error rate and failure/recovery exercises. |
| Operational effort | TBD | Not assessed | Record setup, deployment, monitoring, and rollback effort. |
| Model-quality evidence | TBD or N/A | Not evaluated | Record dataset/split, metric, parity, and limitations. |

Use the shared [comparison dimensions](spike-comparison.md) so results remain comparable across spikes.

## 6. Security and governance

- Record data classification, privacy assessment, approved use, model/system owner, reviewers, and required independent approvals.
- Document least-privilege identities, authentication/authorization, network controls, secrets handling, encryption, audit logging, and retention.
- Scan dependencies, containers, queries, notebooks, and artifacts as applicable; record findings and accepted exceptions.
- Require immutable versions/digests, integrity verification, provenance, signing/attestation, lineage, separation of duties, and traceable promotion evidence where the route to live requires them.
- Assess prompt injection, unsafe tool use, data leakage, content safety, and human oversight for GenAI systems; assess SQL/data access and notebook exfiltration risks for analytical environments.

## 7. Limitations and decision

- List untested assumptions, synthetic or non-representative data, excluded failure modes, platform constraints, and evidence that cannot be generalized.
- State the outcome: **proceed**, **revise and rerun**, **hold**, or **reject**.
- Explain which evidence drove the decision, what remains uncertain, and who accepted the result.
- Update the [spike comparison](spike-comparison.md); do not present a local pass as production approval.

## 8. Route-to-live next step

Name one bounded next step and its owner. Include the target environment and the missing control or evidence it resolves—for example a Cloud Run canary, Vertex batch staging run, governed BigQuery dataset/query deployment, managed Workbench image, GKE Job with production policies, or GenAI gateway/control-plane evaluation.

Before promotion, define CI/CD and infrastructure ownership, immutable artifact storage, environment separation, approvals, monitoring/alerts, service or batch objectives, cost controls, incident response, rollback, evidence retention, and decommissioning. Link the delivery ticket or design; do not implement production infrastructure inside a spike unless separately approved.

## Approach-specific prompts

- **Online FastAPI:** request/version contract, readiness, concurrency, cold starts, latency, authentication, and canary/rollback.
- **Vertex AI batch pipelines:** job specification, input/output locations, orchestration, retries, quotas, partial failure, lineage, and batch duration/cost.
- **BigQuery ML:** dataset boundaries, SQL/model versioning, slot/bytes cost, permissions, reproducibility, evaluation SQL, and export/serving path.
- **Workbench:** image/environment reproducibility, notebook execution order, identity/data access, idle cost, artifact handoff, and removal of manual state.
- **GKE batch:** Job/CronJob semantics, resources, scheduling, autoscaling, retries, checkpointing, workload identity, image policy, and cluster operations.
- **GenAI control plane:** model/provider routing, prompt/tool versions, evaluation sets, guardrails, policy enforcement, telemetry/redaction, rate limits, fallback, and human review.
