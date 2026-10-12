import hashlib
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

import joblib

from app.config import MODEL_PATH

logger = logging.getLogger(__name__)


@lru_cache(maxsize=4)
def _load_pipeline(path: str, modified_ns: int, size: int) -> Optional[Any]:
    model_path = Path(path)
    if modified_ns < 0:
        logger.error("Model artifact does not exist at configured path: %s", model_path)
        return None

    try:
        pipeline = joblib.load(model_path)
        if (
            not hasattr(pipeline, "named_steps")
            or "tfidf" not in pipeline.named_steps
            or "classifier" not in pipeline.named_steps
        ):
            raise ValueError("Saved model is not a valid TF-IDF classifier pipeline.")
    except Exception as exc:
        logger.exception(
            "Unable to load model artifact at %s (%s): %s",
            model_path,
            type(exc).__name__,
            exc,
        )
        return None

    logger.info("Loaded spam classification model from %s (%d bytes)", model_path, size)
    return pipeline


def load_pipeline() -> Optional[Any]:
    model_path = Path(MODEL_PATH).expanduser()
    if not model_path.is_absolute():
        model_path = Path(__file__).resolve().parents[2] / model_path
    model_path = model_path.resolve()
    try:
        stat = model_path.stat()
    except FileNotFoundError:
        return _load_pipeline(str(model_path), -1, -1)
    return _load_pipeline(str(model_path), stat.st_mtime_ns, stat.st_size)


def get_model_metadata() -> Dict[str, Any]:
    model_path = Path(MODEL_PATH).expanduser()
    if not model_path.is_absolute():
        model_path = Path(__file__).resolve().parents[2] / model_path
    model_path = model_path.resolve()
    metadata_path = model_path.with_name("model_metadata.json")
    if not metadata_path.exists():
        return {}
    with metadata_path.open("r", encoding="utf-8") as handle:
        metadata = json.load(handle)
    expected_hash = metadata.get("model_artifact_sha256")
    if expected_hash:
        actual_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise RuntimeError("Model artifact checksum does not match the training metadata.")
    pipeline = load_pipeline()
    selected_model = metadata.get("selected_model")
    classifier = pipeline.named_steps["classifier"] if pipeline is not None else None
    actual_model = {
        "LinearSVC": "linear_svc",
        "LogisticRegression": "logistic_regression",
        "MultinomialNB": "naive_bayes",
    }.get(type(classifier).__name__)
    if selected_model and actual_model and selected_model != actual_model:
        raise RuntimeError("Selected model in metadata does not match the loaded model artifact.")
    return metadata
