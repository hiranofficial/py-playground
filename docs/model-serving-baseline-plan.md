# Model-serving baseline plan: FastAPI on GCP

**Status:** Planning only — no serving implementation is included here.

## Purpose and scope

Build the first reproducible path for synchronous, online Python inference: load one versioned model into a FastAPI process, expose a small HTTP API, package it as a container, and run it on Google Cloud Run. The baseline should be simple enough to run locally and structured so the same stateless image can later run on GKE.

## Stable prediction contract

The versioned route and explicit schema form the compatibility boundary. The first model may narrow the `features` fields, but it must not change this envelope without a new API version.

```http
POST /v1/predictions
Content-Type: application/json
```

```json
{
  "request_id": "client-generated-id",
  "instances": [
    {"id": "row-1", "features": {"feature_a": 1.2, "feature_b": 3}}
  ]
}
```

```json
{
  "request_id": "client-generated-id",
  "model_version": "2026-07-24.1",
  "predictions": [
    {"id": "row-1", "value": 0.82}
  ]
}
```

- Accept JSON only, require 1–100 instances, preserve input order, and reject unknown or missing features.
- Use finite JSON numbers and deterministic output serialization; document units, feature ranges, and classification labels with the model.
- Echo a valid client `request_id`; otherwise generate one. Never return partial success for a batch.
- Return errors as `{"request_id":"...","error":{"code":"...","message":"...","details":[]}}`; keep machine-readable codes stable and messages safe for clients.

## Model artifact and lifecycle

- Export an immutable ONNX model (never a pickle/joblib object) plus a separate JSON manifest containing model version, ONNX/runtime versions, ordered feature schema, labels, training-data reference, evaluation summary, and the model file's SHA-256 checksum. Treat both files as one governed package; do not bake secrets into either artifact or image.
- Select the artifact using configuration. For the baseline, copy it into the image for atomic, reproducible revisions; later, a startup download from versioned Cloud Storage may be added without changing the API.
- On process startup: locate the manifest and ONNX file, validate their schema, verify the checksum, create one ONNX Runtime session, run a small self-test, then mark the process ready. A failure leaves readiness false and terminates startup rather than serving with an unknown model.
- Treat model and configuration as read-only after startup. A model update produces a new image/revision and uses Cloud Run traffic shifting for rollback.

## HTTP service behavior

- `GET /healthz`: liveness only; returns `200` while the event loop is responsive and does not call the model or dependencies.
- `GET /readyz`: returns `200` with `model_version` after load and self-test; otherwise `503`.
- `POST /v1/predictions`: validate, transform using the artifact's declared preprocessing, infer, and serialize the versioned response.
- Pydantic schemas reject malformed JSON, extra fields, invalid types, non-finite values, oversized batches, and out-of-range features before inference. Use `400` for malformed JSON, `415` for media type, `422` for schema/domain validation, `503` when not ready, and `500` for unexpected inference failures. Add request/body-size limits at the service edge.

## Configuration and observability

Use environment variables with startup validation for `MODEL_MANIFEST_PATH`, `LOG_LEVEL`, and service limits; derive the model version from the verified manifest and respect Cloud Run's `PORT`. Defaults should support local development, while production configuration stays outside the image.

Emit one structured JSON log per request with timestamp, severity, request ID, route, status, latency in milliseconds, batch size, model version, and revision identifier. Do not log raw feature values or predictions by default. Cloud Logging-derived metrics should track request rate, status/error code, p50/p95/p99 latency, readiness failures, instance count, and model-version/revision traffic; alerts begin with elevated 5xx rate and p95 latency.

## Local delivery and verification

1. Run the app with Uvicorn and a tiny deterministic test artifact; provide example `curl` requests.
2. Add unit tests for schemas, preprocessing, model loading/checksum failure, and prediction mapping; API tests for endpoints and error envelopes; and a container smoke test covering startup, readiness, and one prediction.
3. Build a non-root, minimal container that listens on `$PORT`, pins dependencies, includes health metadata where useful, and shuts down gracefully. Scan dependencies and the image in CI.

## GCP route to live

1. Create a private regional Artifact Registry Docker repository, authenticate CI with short-lived identity, build the image, scan it, and push immutable commit/model tags. Record the image digest.
2. Deploy that digest to Cloud Run as a new immutable revision with a dedicated least-privilege service account, fixed region, CPU/memory, concurrency, timeout, min/max instances, startup/liveness probes, and environment configuration. Keep invocation authenticated unless a reviewed public API requirement says otherwise.
3. Smoke-test the revision without production traffic, shift a small percentage of traffic, watch errors/latency/model-version metrics, then promote or roll back to the prior revision.
4. Automate build, test, push, deploy, and promotion with CI/CD and infrastructure as code. See the official [Artifact Registry push workflow](https://cloud.google.com/artifact-registry/docs/docker/pushing-and-pulling), [Cloud Run deployment guide](https://cloud.google.com/run/docs/deploying), and [container runtime contract](https://cloud.google.com/run/docs/container-contract).

Keep the container stateless, bind configuration through environment variables, expose standard probes, avoid Cloud Run-specific application imports, and publish to Artifact Registry. These choices preserve a later GKE path using the same image plus Deployment, Service, probes, resource requests/limits, autoscaling, and managed ingress.

## Baseline evaluation measures

- **Correctness:** outputs match an offline golden dataset within declared tolerances; schema and preprocessing parity are tested.
- **Model quality:** record task-appropriate metrics (for example accuracy/F1/AUC or MAE/RMSE) and acceptance thresholds in the manifest; compare by model version.
- **Service:** define initial targets after a local load test for p95/p99 latency, sustained throughput, cold-start/readiness time, error rate, and memory at expected and maximum batch sizes.
- **Operations:** demonstrate checksum/load failure handling, rollback to the prior revision, and traceability from response model version to artifact manifest and image digest.

## Minimum security and governance

- Use least-privilege IAM, a dedicated runtime identity, private Artifact Registry, authenticated invocation, TLS at the managed edge, and Secret Manager for any future secrets.
- Pin and scan dependencies/images, retain build provenance and evaluation evidence, and deploy immutable digests. Restrict who can publish artifacts, deploy revisions, or shift traffic.
- Minimize and classify request data; redact logs, set retention, document data residency, and avoid storing payloads by default. Add abuse/rate limits before public exposure.
- Maintain model ownership, approval status, training-data lineage, intended use/limitations, change history, and a rollback owner in the manifest or linked model card.

## Phased milestones

1. **Contract and fixture:** approve schemas, error codes, deterministic artifact/manifest, golden cases, and acceptance measures.
2. **Local service:** implement loading, probes, prediction, validation, structured logs, and automated tests.
3. **Container:** produce and scan a reproducible non-root image; pass container smoke and load tests.
4. **Cloud Run staging:** push to Artifact Registry, deploy by digest with IAM/configuration, and verify dashboards, alerts, and rollback.
5. **Controlled production:** canary, evaluate service/model measures, promote, and record evidence and runbook ownership.

## Non-goals

This baseline does not include training pipelines, a feature store, asynchronous or streaming inference, GPU serving, multi-model routing, online model reloads, automated drift detection/retraining, a public UI, GKE deployment, or a general-purpose ML platform. Those require separate evidence and design decisions after the baseline is measured.
