import argparse
import hashlib
import json
from pathlib import Path

import sklearn
import skl2onnx
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

from app.model_service import FEATURE_NAMES


DEFAULT_VERSION = "iris-logreg-v1"
ONNX_OPSET = 17


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def train_and_save(
    output_dir: Path, model_version: str = DEFAULT_VERSION
) -> Path:
    iris = load_iris()
    classifier = LogisticRegression(max_iter=500, random_state=42)
    estimator = Pipeline(
        [
            ("scale", StandardScaler()),
            ("classifier", classifier),
        ]
    )
    estimator.fit(iris.data, iris.target)

    onnx_model = convert_sklearn(
        estimator,
        initial_types=[("features", FloatTensorType([None, len(FEATURE_NAMES)]))],
        options={id(classifier): {"zipmap": False}},
        target_opset=ONNX_OPSET,
    )
    model_bytes = onnx_model.SerializeToString()
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / f"{model_version}.onnx"
    manifest_path = output_dir / f"{model_version}.json"
    model_path.write_bytes(model_bytes)

    manifest = {
        "schema_version": 1,
        "artifact_version": model_version,
        "artifact": {
            "file": model_path.name,
            "format": "onnx",
            "opset": ONNX_OPSET,
            "sha256": _sha256(model_bytes),
        },
        "features": [
            {"order": index, "name": name, "dtype": "float32", "unit": "cm"}
            for index, name in enumerate(FEATURE_NAMES)
        ],
        "labels": [
            {"class_id": index, "name": str(name)}
            for index, name in enumerate(iris.target_names)
        ],
        "training_data": {
            "name": "scikit-learn built-in Iris dataset",
            "reference": "https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_iris.html",
        },
        "runtime": {
            "input_name": onnx_model.graph.input[0].name,
            "label_output": onnx_model.graph.output[0].name,
            "probabilities_output": onnx_model.graph.output[1].name,
        },
        "producer": {
            "scikit_learn_version": sklearn.__version__,
            "skl2onnx_version": skl2onnx.__version__,
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train and export the Iris logistic regression model to ONNX"
    )
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument("--output-dir", type=Path, default=Path("models"))
    args = parser.parse_args()
    manifest_path = train_and_save(args.output_dir, args.version)
    print(f"Saved {args.version} package to {manifest_path.parent}")


if __name__ == "__main__":
    main()
