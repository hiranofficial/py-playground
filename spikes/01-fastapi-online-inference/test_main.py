import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.model_service import ModelService
from train_model import train_and_save


@pytest.fixture
def client(tmp_path, monkeypatch):
    manifest_path = train_and_save(tmp_path, model_version="iris-test-v1")
    monkeypatch.setenv("MODEL_MANIFEST_PATH", str(manifest_path))
    with TestClient(create_app()) as test_client:
        yield test_client


def test_health_and_readiness(client):
    assert client.get("/healthz").json() == {"status": "healthy"}
    readiness = client.get("/readyz")
    assert readiness.status_code == 200
    assert readiness.json() == {"status": "ready", "model_version": "iris-test-v1"}


def test_predicts_iris_species_with_probabilities(client):
    response = client.post(
        "/v1/predictions",
        json={
            "request_id": "test-request-1",
            "instances": [
                {
                    "id": "flower-1",
                    "features": {
                        "sepal_length_cm": 5.1,
                        "sepal_width_cm": 3.5,
                        "petal_length_cm": 1.4,
                        "petal_width_cm": 0.2,
                    },
                }
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["request_id"] == "test-request-1"
    assert body["model_version"] == "iris-test-v1"
    assert body["predictions"][0]["id"] == "flower-1"
    assert body["predictions"][0]["species"] == "setosa"
    assert set(body["predictions"][0]["probabilities"]) == {
        "setosa",
        "versicolor",
        "virginica",
    }
    assert sum(body["predictions"][0]["probabilities"].values()) == pytest.approx(
        1.0, abs=2e-6
    )
    assert body["metadata"]["latency_ms"] >= 0


def test_rejects_invalid_measurement_without_echoing_input(client):
    response = client.post(
        "/v1/predictions",
        json={
            "request_id": "invalid-request",
            "instances": [
                {
                    "id": "flower-1",
                    "features": {
                        "sepal_length_cm": -1.0,
                        "sepal_width_cm": 3.5,
                        "petal_length_cm": 1.4,
                        "petal_width_cm": 0.2,
                    },
                }
            ],
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["request_id"] == "invalid-request"
    assert body["error"]["code"] == "INVALID_REQUEST"
    assert body["error"]["message"] == "Request validation failed"
    assert "-1.0" not in response.text


def test_rejects_model_when_checksum_does_not_match(tmp_path):
    manifest_path = train_and_save(tmp_path, model_version="tampered-v1")
    (tmp_path / "tampered-v1.onnx").write_bytes(b"not the approved model")

    with pytest.raises(ValueError, match="checksum does not match"):
        ModelService.load(manifest_path)
