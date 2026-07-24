# Iris classifier API

This local route-to-live spike trains a genuine scikit-learn logistic regression classifier on the built-in Iris dataset, exports it to portable ONNX, and serves it with ONNX Runtime and FastAPI. It is an engineering baseline, **not a production-approved financial-institution service or model**.

## Model package

Training writes two files under `models/`:

- `iris-logreg-v1.onnx`: executable, language-neutral model graph; no pickle/joblib objects are loaded.
- `iris-logreg-v1.json`: separate manifest with the artifact version, ordered feature schema, class labels, training-data reference, runtime tensor names, producer versions, and the ONNX file's SHA-256 checksum.

Startup reads `MODEL_MANIFEST_PATH` (default `models/iris-logreg-v1.json`), validates the manifest and feature order, verifies the ONNX checksum, creates an ONNX Runtime session, and performs a self-test before readiness succeeds. Treat the manifest and model as one immutable package.

## Run locally

From the repository root, enter this self-contained spike, then use Python 3.12 or newer:

```bash
cd spikes/01-fastapi-online-inference
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python train_model.py
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
curl -X POST http://localhost:8000/v1/predictions \
  -H 'Content-Type: application/json' \
  -d '{
    "request_id": "example-1",
    "instances": [{
      "id": "flower-1",
      "features": {
        "sepal_length_cm": 5.1,
        "sepal_width_cm": 3.5,
        "petal_length_cm": 1.4,
        "petal_width_cm": 0.2
      }
    }]
  }'
```

To create another immutable version and select it explicitly:

```bash
python train_model.py --version iris-logreg-v2
MODEL_MANIFEST_PATH=models/iris-logreg-v2.json uvicorn app.main:app --port 8000
```

## Test

From `spikes/01-fastapi-online-inference/` with the virtual environment active:

```bash
pytest -q
```

Tests export isolated ONNX packages and cover health, readiness, a representative prediction, probabilities, model metadata, safe validation errors, and rejection of a model whose checksum does not match its manifest.

## Container and route to live

From `spikes/01-fastapi-online-inference/`, the image trains the deterministic package during the build and runs as a non-root user. Compose resolves its `build: .` context to this spike directory:

```bash
docker compose up --build
```

The API is then available at `http://localhost:8000`. The image listens on `PORT` (default `8080`) for Cloud Run compatibility.

For a real route to live, build the model and service through controlled CI, retain test and approval evidence, scan dependencies and the image, and publish the immutable container/model package to private Artifact Registry. Deploy by image digest—not a mutable tag—and apply organization-approved signing, signature verification, provenance/attestation, separation of duties, model inventory/ownership, data lineage, validation, change approval, monitoring, retention, and rollback controls. Those controls and independent risk/governance approval are outside this local spike; passing these tests must not be interpreted as production approval.
