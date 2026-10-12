import hashlib
import json
from pathlib import Path

import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi

DATASET_ID = "uciml/sms-spam-collection-dataset"


def download_kaggle_sms_spam():
    target_dir = Path(__file__).resolve().parents[2] / "data" / "raw"
    target_dir.mkdir(parents=True, exist_ok=True)
    staging_dir = target_dir / "kaggle_download"
    staging_dir.mkdir(exist_ok=True)

    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(DATASET_ID, path=str(staging_dir), unzip=True, quiet=False)

    csv_candidates = sorted(staging_dir.rglob("*.csv"))
    source = None
    for candidate in csv_candidates:
        try:
            frame = pd.read_csv(candidate, encoding="latin-1", nrows=1)
        except (OSError, UnicodeError, pd.errors.ParserError):
            continue
        if {"v1", "v2"}.issubset({str(column).strip().lower() for column in frame.columns}):
            source = candidate
            break
    if source is None:
        raise FileNotFoundError(f"Kaggle dataset {DATASET_ID} downloaded, but no v1/v2 CSV was found.")

    target = target_dir / "spam.csv"
    target.write_bytes(source.read_bytes())
    marker = {
        "dataset_id": DATASET_ID,
        "file_name": target.name,
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
    }
    (target_dir / ".kaggle_sms_collection.json").write_text(json.dumps(marker, indent=2), encoding="utf-8")
    print(f"Downloaded Kaggle dataset {DATASET_ID} to {target}")


if __name__ == "__main__":
    download_kaggle_sms_spam()
