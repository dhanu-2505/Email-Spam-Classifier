import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import MAX_BATCH_SIZE, MAX_MESSAGE_LENGTH
from app.schemas import BatchPredictRequest, PredictRequest, PredictResponse
from app.services.model_service import get_model_metadata, load_pipeline
from app.services.prediction_service import classify_message, get_keyword_insights
from app.dependencies import require_user

logger = logging.getLogger("spam_api")
router = APIRouter()


@router.get("/health")
def health() -> Dict[str, Any]:
    model = load_pipeline()
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "backend": "FastAPI",
    }


@router.get("/api/model-info", dependencies=[Depends(require_user)])
def model_info() -> Dict[str, Any]:
    metadata = get_model_metadata()
    if not metadata:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model metadata is not available.")
    return metadata


@router.post("/api/predict", response_model=PredictResponse, dependencies=[Depends(require_user)])
def predict(payload: PredictRequest) -> PredictResponse:
    text = payload.message.strip()
    if not text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message text cannot be empty.")
    if len(text) > MAX_MESSAGE_LENGTH:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"Message exceeds {MAX_MESSAGE_LENGTH} characters.")

    result = classify_message(text)
    if not result:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model is not available; retraining is required.")
    return PredictResponse(**result)


@router.post("/api/predict/batch", dependencies=[Depends(require_user)])
def predict_batch(payload: BatchPredictRequest) -> Dict[str, Any]:
    if len(payload.messages) > MAX_BATCH_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Batch size cannot exceed {MAX_BATCH_SIZE} messages.")

    results: List[Dict[str, Any]] = []
    for message in payload.messages:
        text = message.strip()
        if not text:
            results.append({"error": "empty message", "index": len(results)})
            continue
        if len(text) > MAX_MESSAGE_LENGTH:
            results.append({"error": f"message too long ({len(text)} > {MAX_MESSAGE_LENGTH})", "index": len(results)})
            continue
        result = classify_message(text)
        if not result:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Prediction service is unavailable.")
        results.append({"index": len(results), "result": result})

    return {"results": results}


@router.get("/api/analytics", dependencies=[Depends(require_user)])
def analytics() -> Dict[str, Any]:
    metadata = get_model_metadata()
    if not metadata:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Evaluation data is unavailable.")
    return {
        "dataset": metadata.get("dataset", {}),
        "selected_model": metadata.get("selected_model"),
        "evaluation": metadata.get("evaluation", {}),
        "comparison": metadata.get("comparison", []),
        "training_info": metadata.get("training_info", {}),
    }


@router.get("/api/keywords", dependencies=[Depends(require_user)])
def keywords() -> Dict[str, Any]:
    insights = get_keyword_insights()
    if not insights:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Keyword insights are unavailable.")
    return {"keywords": insights}


@router.get("/api/history", dependencies=[Depends(require_user)])
def prediction_history() -> Dict[str, Any]:
    return {
        "history": [],
        "scope": "frontend_session",
        "message": "Prediction history is intentionally kept in frontend memory and is not persisted by the backend.",
    }
