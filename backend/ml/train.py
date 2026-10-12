import json
import hashlib
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB

from backend.ml.data_loader import find_dataset, load_dataset, validate_and_prepare_dataset, verify_kaggle_download
from backend.ml.eda import create_eda_reports
from backend.ml.preprocess import normalize_text

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def build_pipeline(model_name: str) -> Pipeline:
    if model_name == "naive_bayes":
        return Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, strip_accents="unicode")),
            ("classifier", MultinomialNB(alpha=0.1)),
        ])
    if model_name == "logistic_regression":
        return Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, strip_accents="unicode")),
            ("classifier", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)),
        ])
    if model_name == "linear_svc":
        return Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, strip_accents="unicode")),
            ("classifier", LinearSVC(class_weight="balanced", random_state=42)),
        ])
    raise ValueError(f"Unsupported model: {model_name}")


def train_and_evaluate() -> dict:
    dataset_path = find_dataset()
    if dataset_path is None:
        raise FileNotFoundError("No dataset found. Place a CSV/TSV file in data/raw.")
    if dataset_path.name.lower() == "spam.csv" and not verify_kaggle_download(dataset_path):
        raise ValueError(
            "Kaggle CSV provenance is not verified. Download the approved dataset with "
            "backend/ml/download_dataset.py before training."
        )

    raw_df = load_dataset(str(dataset_path))
    prepared = validate_and_prepare_dataset(raw_df)
    prepared["text"] = prepared["text"].apply(normalize_text)
    X = prepared["text"]
    y = prepared["label"]
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    reports_dir = Path(__file__).resolve().parents[2] / "reports"
    plots = create_eda_reports(prepared, output_dir=str(reports_dir))
    comparison = []
    best_key = None
    best_score = -1

    for model_name in ["naive_bayes", "logistic_regression", "linear_svc"]:
        pipeline = build_pipeline(model_name)
        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)
        metrics = {
            "accuracy": accuracy_score(y_test, preds),
            "precision": precision_score(y_test, preds, pos_label="spam", zero_division=0),
            "recall": recall_score(y_test, preds, pos_label="spam", zero_division=0),
            "f1": f1_score(y_test, preds, pos_label="spam", zero_division=0),
        }
        matrix = confusion_matrix(y_test, preds, labels=["ham", "spam"])
        tn, fp, fn, tp = matrix.ravel()
        metrics.update({
            "false_positive_rate": float(fp / (fp + tn)) if (fp + tn) else 0.0,
            "false_negative_rate": float(fn / (fn + tp)) if (fn + tp) else 0.0,
            "confusion_matrix": matrix.tolist(),
        })
        comparison.append({"model": model_name, **metrics})
        if metrics["f1"] > best_score:
            best_score = metrics["f1"]
            best_key = model_name

        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=3, scoring="f1_macro")
        print(f"{model_name}: {metrics} | cv_mean={cv_scores.mean():.4f}")

    selected_model = best_key or "logistic_regression"
    final_pipeline = build_pipeline(selected_model)
    final_pipeline.fit(X, y)
    model_path = MODEL_DIR / "spam_classifier.joblib"
    joblib.dump(final_pipeline, model_path)
    dataset_sha256 = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
    is_kaggle_download = dataset_path.name.lower() == "spam.csv" and verify_kaggle_download(dataset_path)

    metadata = {
        "dataset": {
            "source": str(dataset_path.relative_to(Path(__file__).resolve().parents[2])),
            "source_sha256": dataset_sha256,
            "source_type": "Kaggle API download" if is_kaggle_download else (
                "Kaggle-format SMS CSV; download provenance unverified"
                if dataset_path.name.lower() == "spam.csv"
                else "UCI archive copy"
            ),
            "dataset_type": (
                "SMS messages (Kaggle SMS Spam Collection)"
                if is_kaggle_download
                else "SMS messages (Kaggle-compatible CSV; provenance unverified)"
                if dataset_path.name.lower() == "spam.csv"
                else "SMS messages (UCI SMS Spam Collection)"
                if dataset_path.name == "SMSSpamCollection.tsv"
                else "Email messages (SpamAssassin public corpus)"
            ),
            "kaggle_dataset_id": "uciml/sms-spam-collection-dataset" if is_kaggle_download else None,
            "kaggle_download_verified": is_kaggle_download,
            "kaggle_url": "https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset" if is_kaggle_download else None,
            "rows": int(len(prepared)),
            "spam_count": int((prepared["label"] == "spam").sum()),
            "ham_count": int((prepared["label"] == "ham").sum()),
        },
        "selected_model": selected_model,
        "model_artifact_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
        "comparison": comparison,
        "training_info": {
            "random_state": 42,
            "test_size": 0.2,
            "stratified": True,
            "evaluation_data": "stratified held-out test split (20%)",
            "feature_engineering": "TF-IDF (1-2 grams)",
        },
        "evaluation": next(
            {
                key: round(float(value), 4)
                for key, value in selected.items()
                if key in {"accuracy", "precision", "recall", "f1"}
            }
            for selected in comparison
            if selected["model"] == selected_model
        ),
    }
    with (MODEL_DIR / "model_metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)

    return metadata


if __name__ == "__main__":
    train_and_evaluate()
