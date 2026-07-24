import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import onnxruntime as ort

from app.models import IrisFeatures


FEATURE_NAMES = (
    "sepal_length_cm",
    "sepal_width_cm",
    "petal_length_cm",
    "petal_width_cm",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as model_file:
        for chunk in iter(lambda: model_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class ModelService:
    session: ort.InferenceSession
    model_version: str
    target_names: tuple[str, ...]
    input_name: str
    label_output: str
    probabilities_output: str

    @classmethod
    def load(cls, manifest_path: Path) -> "ModelService":
        if not manifest_path.is_file():
            raise FileNotFoundError(
                f"Model manifest not found at {manifest_path}. Run train_model.py first."
            )

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            artifact = manifest["artifact"]
            feature_names = tuple(item["name"] for item in manifest["features"])
            labels = tuple(
                item["name"]
                for item in sorted(manifest["labels"], key=lambda item: item["class_id"])
            )
            runtime = manifest["runtime"]
            model_version = str(manifest["artifact_version"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("Model manifest has an invalid format") from exc

        if manifest.get("schema_version") != 1 or artifact.get("format") != "onnx":
            raise ValueError("Model manifest has an unsupported schema or format")
        if feature_names != FEATURE_NAMES:
            raise ValueError("Model manifest feature schema does not match the API")
        if not labels or [item["class_id"] for item in manifest["labels"]] != list(
            range(len(labels))
        ):
            raise ValueError("Model manifest labels are invalid")

        model_filename = artifact.get("file")
        if not isinstance(model_filename, str) or Path(model_filename).name != model_filename:
            raise ValueError("Model manifest artifact path is invalid")
        model_path = manifest_path.parent / model_filename
        if not model_path.is_file():
            raise FileNotFoundError("ONNX model referenced by the manifest was not found")
        if _sha256(model_path) != artifact.get("sha256"):
            raise ValueError("ONNX model checksum does not match the manifest")

        session = ort.InferenceSession(
            str(model_path), providers=["CPUExecutionProvider"]
        )
        service = cls(
            session=session,
            model_version=model_version,
            target_names=labels,
            input_name=str(runtime["input_name"]),
            label_output=str(runtime["label_output"]),
            probabilities_output=str(runtime["probabilities_output"]),
        )
        service._run(np.asarray([[5.1, 3.5, 1.4, 0.2]], dtype=np.float32))
        return service

    def _run(self, values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        labels, probabilities = self.session.run(
            [self.label_output, self.probabilities_output],
            {self.input_name: values},
        )
        return labels, probabilities

    def predict(self, features: IrisFeatures) -> tuple[str, dict[str, float]]:
        values = np.asarray(
            [[getattr(features, name) for name in FEATURE_NAMES]], dtype=np.float32
        )
        labels, raw_probabilities = self._run(values)
        predicted_class = int(labels[0])
        probabilities = {
            name: round(float(probability), 6)
            for name, probability in zip(
                self.target_names, raw_probabilities[0], strict=True
            )
        }
        return self.target_names[predicted_class], probabilities
