import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.api.auth import router as auth_router
from app.config import CORS_ORIGINS, HOST, LOG_LEVEL, MODEL_PATH, PORT
from app.services.model_service import load_pipeline

logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    model_path = Path(MODEL_PATH).expanduser().resolve()
    logger.info("Loading model artifact from %s", model_path)
    pipeline = load_pipeline()
    logger.info("Model startup check: path=%s loaded=%s", model_path, pipeline is not None)
    yield


app = FastAPI(
    title="Email Spam Classifier API",
    version="1.0.0",
    description="Spam and ham message prediction API. The current model is trained on SMS messages.",
    lifespan=lifespan,
)

origins = [origin.strip() for origin in CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_, exc: RequestValidationError) -> JSONResponse:
    errors = [
        {key: value for key, value in error.items() if key != "input"}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(errors)},
    )


@app.get("/")
def root() -> dict[str, Any]:
    return {"message": "Email Spam Classifier API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False)
