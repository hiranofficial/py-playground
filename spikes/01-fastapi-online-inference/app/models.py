from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


Measurement = Annotated[float, Field(strict=True, gt=0, le=10)]


class IrisFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sepal_length_cm: Measurement
    sepal_width_cm: Measurement
    petal_length_cm: Measurement
    petal_width_cm: Measurement


class PredictionInstance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=128)
    features: IrisFeatures


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str | None = Field(default=None, min_length=1, max_length=128)
    instances: list[PredictionInstance] = Field(min_length=1, max_length=100)


class Prediction(BaseModel):
    id: str
    species: str
    probabilities: dict[str, float]


class PredictionMetadata(BaseModel):
    latency_ms: float


class PredictionResponse(BaseModel):
    request_id: str
    model_version: str
    predictions: list[Prediction]
    metadata: PredictionMetadata
