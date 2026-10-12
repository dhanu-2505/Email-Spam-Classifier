import re
from typing import Any, Dict, List, Optional

import numpy as np

from app.services.model_service import load_pipeline


def _normalize_text(text: str) -> str:
    value = text or ""
    value = value.replace("\r", " ").replace("\n", " ")
    value = re.sub(r"https?://\S+|www\.\S+", " URL ", value, flags=re.IGNORECASE)
    value = re.sub(r"\s+", " ", value).strip()
    return value.lower()


def classify_message(message: str) -> Optional[Dict[str, Any]]:
    model = load_pipeline()
    if model is None:
        return None

    cleaned = _normalize_text(message)
    prediction = model.predict([cleaned])[0]
    probability = None
    if hasattr(model, "predict_proba"):
        probability = model.predict_proba([cleaned])[0]
        proba = float(probability[np.argmax(probability)]) if len(probability) > 0 else None
    else:
        proba = None

    label = str(prediction).strip().lower()
    explanation = "This message was classified using the trained text classifier and TF-IDF features."
    if label == "spam":
        explanation = "The message contains patterns commonly associated with spam, such as promotional language, urgency, or suspicious solicitation."
    else:
        explanation = "The message looks more like legitimate communication based on the learned feature patterns."

    top_features = get_top_features(cleaned, label)
    result = {
        "label": label,
        "confidence": round(float(proba), 4) if proba is not None else None,
        "explanation": explanation,
        "top_features": top_features,
    }

    return result


def get_top_features(message: str, predicted_label: str) -> List[str]:
    model = load_pipeline()
    if model is None:
        return []
    transformer = getattr(model, "named_steps", {}).get("tfidf")
    classifier = getattr(model, "named_steps", {}).get("classifier")
    if transformer is None or classifier is None:
        return []

    feature_names = transformer.get_feature_names_out()
    tfidf_vector = transformer.transform([_normalize_text(message)])
    weights = classifier.coef_
    if len(weights.shape) == 1:
        weights = weights.reshape(1, -1)

    class_index = 0
    if hasattr(classifier, "classes_") and len(classifier.classes_) > 0:
        labels = list(classifier.classes_)
        if predicted_label in labels:
            class_index = labels.index(predicted_label)

    if weights.shape[0] == 1 and predicted_label == "ham":
        scores = -weights[0]
    else:
        scores = weights[0 if weights.shape[0] == 1 else class_index]
    ranked_indices = np.argsort(scores)[::-1][:10]
    tagged = []
    for idx in ranked_indices:
        if idx < len(feature_names) and tfidf_vector[0, idx] > 0:
            token = feature_names[idx]
            tagged.append(token)
    return tagged[:5]


def get_keyword_insights() -> Dict[str, List[str]]:
    model = load_pipeline()
    if model is None:
        return {}
    transformer = getattr(model, "named_steps", {}).get("tfidf")
    classifier = getattr(model, "named_steps", {}).get("classifier")
    if transformer is None or classifier is None:
        return {}

    names = transformer.get_feature_names_out()
    coef = classifier.coef_
    if len(coef.shape) == 1:
        coef = coef.reshape(1, -1)
    labels = getattr(classifier, "classes_", ["ham", "spam"])
    if len(labels) == 2:
        spam_index = 1 if "spam" in labels else 0
        ham_index = 0 if "ham" in labels else 1
    else:
        spam_index = 0
        ham_index = 0

    if coef.shape[0] == 1:
        spam_index = 0
        ham_index = 0

    spam_terms = [names[i] for i in np.argsort(coef[spam_index])[::-1][:15]]
    ham_terms = [names[i] for i in np.argsort(coef[ham_index])[:15]]
    return {"spam_terms": spam_terms, "ham_terms": ham_terms}
