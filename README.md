# py-playground

This repository is a sandbox for independent Python experiments. Each spike lives under `spikes/` and owns its application code, dependencies, tests, container configuration, generated artifacts, and usage guide. Run commands from the spike directory unless its README says otherwise; spikes should not import code from one another.

## Spikes

1. [FastAPI online inference](spikes/01-fastapi-online-inference/README.md) — trains a scikit-learn Iris logistic regression model, exports an ONNX model plus checksummed manifest, and serves predictions with FastAPI and ONNX Runtime.

Use the reusable [spike framework](docs/spike-framework.md) to define and conclude each experiment. Record comparable evidence in the [spike comparison](docs/spike-comparison.md) as more approaches are added.

## Quick start: spike 01

```bash
cd spikes/01-fastapi-online-inference
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python train_model.py
pytest -q
uvicorn app.main:app --reload --port 8000
```

See the spike README for request examples, alternate model versions, and Docker Compose usage.
