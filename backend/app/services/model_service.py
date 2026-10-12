import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional

import joblib

from app.config import MODEL_PATH


def load_pipeline() -> Optional[Any]:
    model_path = Path(MODEL_PATH)
    if not model_path.exists():
        return None
    pipeline = joblib.load(model_path)
    if not hasattr(pipeline, "named_steps") or "tfidf" not in pipeline.named_steps or "classifier" not in pipeline.named_steps:
        raise RuntimeError("Saved model is not a valid TF-IDF classifier pipeline.")
    return pipeline


def get_model_metadata() -> Dict[str, Any]:
    model_path = Path(MODEL_PATH)
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
