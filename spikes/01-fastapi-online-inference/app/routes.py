import json
import logging
from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.models import PredictionRequest, PredictionResponse


router = APIRouter()
logger = logging.getLogger("iris_api")


@router.get("/healthz", tags=["Operations"])
def health() -> dict[str, str]:
    return {"status": "healthy"}


@router.get("/readyz", tags=["Operations"])
def readiness(request: Request):
    service = getattr(request.app.state, "model_service", None)
    if service is None:
        return JSONResponse(
            status_code=503,
            content={"error": {"code": "NOT_READY", "message": "Model is not ready"}},
        )
    return {"status": "ready", "model_version": service.model_version}


@router.post(
    "/v1/predictions",
    response_model=PredictionResponse,
    tags=["Predictions"],
)
def predict(payload: PredictionRequest, request: Request):
    request_id = payload.request_id or str(uuid4())
    service = getattr(request.app.state, "model_service", None)
    if service is None:
        return JSONResponse(
            status_code=503,
            content={
                "request_id": request_id,
                "error": {"code": "NOT_READY", "message": "Model is not ready"},
            },
        )

    started = perf_counter()
    try:
        predictions = []
        for instance in payload.instances:
            species, probabilities = service.predict(instance.features)
            predictions.append(
                {"id": instance.id, "species": species, "probabilities": probabilities}
            )
    except Exception:
        logger.exception("Prediction failed", extra={"request_id": request_id})
        return JSONResponse(
            status_code=500,
            content={
                "request_id": request_id,
                "error": {
                    "code": "INFERENCE_ERROR",
                    "message": "Prediction could not be completed",
                },
            },
        )

    latency_ms = round((perf_counter() - started) * 1000, 3)
    logger.info(
        json.dumps(
            {
                "event": "prediction_completed",
                "request_id": request_id,
                "status": 200,
                "latency_ms": latency_ms,
                "batch_size": len(payload.instances),
                "model_version": service.model_version,
            }
        )
    )
    return {
        "request_id": request_id,
        "model_version": service.model_version,
        "predictions": predictions,
        "metadata": {"latency_ms": latency_ms},
    }
