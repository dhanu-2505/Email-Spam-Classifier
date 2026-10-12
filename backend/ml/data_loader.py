import os
import json
import hashlib
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Optional

import pandas as pd

DATASET_DIR = Path(__file__).resolve().parents[2] / "data"
UCI_SMS_FILENAME = "SMSSpamCollection.tsv"
KAGGLE_SMS_FILENAME = "spam.csv"
KAGGLE_PROVENANCE_FILENAME = ".kaggle_sms_collection.json"
SPAMASSASSIN_DIRNAME = "spamassassin"
SPAMASSASSIN_LABEL_DIRS = {"spam", "spam_2", "easy_ham", "hard_ham", "easy_ham_2"}


def find_dataset() -> Optional[Path]:
    candidates = [
        DATASET_DIR / "raw" / KAGGLE_SMS_FILENAME,
        DATASET_DIR / "raw" / UCI_SMS_FILENAME,
        DATASET_DIR / "raw" / SPAMASSASSIN_DIRNAME,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def load_dataset(path: Optional[str] = None) -> pd.DataFrame:
    dataset_path = Path(path) if path else find_dataset()
    if dataset_path is None:
        raise FileNotFoundError("No dataset found in data/raw or data/processed. Add the dataset and rerun training.")

    if dataset_path.is_dir() and dataset_path.name.lower() == SPAMASSASSIN_DIRNAME:
        records = []
        for label_dir in sorted(SPAMASSASSIN_LABEL_DIRS):
            folder = dataset_path / label_dir
            if not folder.is_dir():
                continue
            label = "spam" if label_dir.startswith("spam") else "ham"
            for message_path in folder.iterdir():
                if not message_path.is_file():
                    continue
                with message_path.open("rb") as handle:
                    message = BytesParser(policy=policy.default).parse(handle)
                body = message.get_body(preferencelist=("plain", "html"))
                text = body.get_content() if body else message.get_payload(decode=True)
                if isinstance(text, bytes):
                    text = text.decode("utf-8", errors="replace")
                records.append({"text": str(text or ""), "label": label})
        return pd.DataFrame(records)
    if dataset_path.name.lower() == KAGGLE_SMS_FILENAME:
        df = pd.read_csv(dataset_path, encoding="latin-1")
        columns = {str(column).strip().lower(): column for column in df.columns}
        label_column = columns.get("v1") or columns.get("label")
        text_column = columns.get("v2") or columns.get("text")
        if label_column is None or text_column is None:
            raise ValueError("Kaggle SMS CSV must contain v1/v2 or label/text columns.")
        return df[[label_column, text_column]].rename(columns={label_column: "label", text_column: "text"})
    if dataset_path.name == UCI_SMS_FILENAME:
        return pd.read_csv(dataset_path, sep="\t", header=None, names=["label", "text"])
    raise ValueError("Only the UCI SMS Spam Collection or SpamAssassin dataset is supported.")


def verify_kaggle_download(dataset_path: Path) -> bool:
    marker_path = dataset_path.parent / KAGGLE_PROVENANCE_FILENAME
    if not marker_path.is_file():
        return False
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    expected_hash = marker.get("sha256")
    if marker.get("dataset_id") != "uciml/sms-spam-collection-dataset" or not expected_hash:
        return False
    actual_hash = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
    return actual_hash == expected_hash


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [str(col).strip().lower() for col in normalized.columns]
    return normalized


def validate_and_prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        raise ValueError("Dataset is empty.")

    df = normalize_columns(df)
    label_candidates = ["label", "spam", "is_spam", "class", "target", 0, 1]
    text_candidates = ["text", "message", "sms", "email", "content", "body", 0, 1]
    found_label = next((col for col in label_candidates if col in df.columns), None)
    found_text = next((col for col in text_candidates if col in df.columns and col != found_label), None)

    if not found_label or not found_text:
        raise ValueError("Dataset must be the UCI SMS Spam Collection or SpamAssassin dataset.")

    clean = df[[found_text, found_label]].copy()
    clean.columns = ["text", "label"]
    clean["text"] = clean["text"].fillna("").astype(str)
    clean["label"] = clean["label"].fillna("ham").astype(str).str.strip().str.lower()
    clean = clean[clean["text"].str.strip() != ""].copy()
    clean = clean[~clean["label"].isin(["", "nan", "none", "null"])].copy()
    clean["label"] = clean["label"].map({"spam": "spam", "ham": "ham", "1": "spam", "0": "ham", "yes": "spam", "no": "ham"})
    clean = clean.dropna(subset=["text", "label"])
    clean = clean.drop_duplicates().reset_index(drop=True)
    if clean.empty:
        raise ValueError("No valid rows remain after validation.")
    return clean
