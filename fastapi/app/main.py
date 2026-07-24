import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.model_service import ModelService
from app.routes import router


DEFAULT_MANIFEST_PATH = (
    Path(__file__).resolve().parents[1] / "models" / "iris-logreg-v1.json"
)


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        manifest_path = Path(
            os.getenv("MODEL_MANIFEST_PATH", str(DEFAULT_MANIFEST_PATH))
        )
        application.state.model_service = ModelService.load(manifest_path)
        yield
        application.state.model_service = None

    application = FastAPI(title="Iris Model Serving Baseline", lifespan=lifespan)

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        body = exc.body if isinstance(exc.body, dict) else {}
        request_id = body.get("request_id") if isinstance(body, dict) else None
        details = [
            {
                "location": [str(part) for part in error["loc"]],
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors()
        ]
        content = {
            "error": {
                "code": "INVALID_REQUEST",
                "message": "Request validation failed",
                "details": details,
            }
        }
        if request_id:
            content["request_id"] = request_id
        return JSONResponse(status_code=422, content=content)

    @application.get("/", tags=["Operations"])
    def root() -> dict[str, str]:
        return {"message": "Welcome to FastAPI Sample!"}

    application.include_router(router)
    return application


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
app = create_app()
