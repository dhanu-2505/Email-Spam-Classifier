# Email Spam Classifier

A full-stack machine-learning demonstrator for spam and ham **message text**, with a FastAPI backend and React frontend. The currently available local corpus contains SMS messages; this project does not claim that its model was trained on real email.

## Verified status

- Current raw file: `data\raw\SMSSpamCollection.tsv`, 5,572 parsed rows (`ham`: 4,825; `spam`: 747), SHA-256 `55341228082b25b832a5868a5ab4b038142a57f70c676c123280af6ff457fe46`.
- The file is an extracted UCI archive copy. Kaggle API credentials and the exact Kaggle archive are not present locally, so the file's Kaggle-download provenance has **not** been verified.
- The selected saved pipeline is scikit-learn `TfidfVectorizer` + `LinearSVC`. Training evaluation uses a stratified held-out 20% test split.
- The API and frontend have been exercised locally. Public deployment is pending and no public URL is claimed.
- The UI is split by public/auth/dashboard/feature routes; the Analytics page loads Recharts only when that feature is selected.

## Project structure

- `backend\` — FastAPI API, authentication, model loading, and training
- `frontend\` — React, TypeScript, Vite, and dashboard pages
- `data\raw\` — local-only source datasets
- `backend\models\` — deployable model and metadata; user database is local/runtime data
- `render.yaml` — Render backend service blueprint

## Dataset provenance and supported inputs

The requested Kaggle dataset is [`uciml/sms-spam-collection-dataset`](https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset). The loader supports:

1. Kaggle's SMS CSV (`spam.csv`, `v1`/`v2` columns).
2. UCI SMS Spam Collection's `SMSSpamCollection.tsv`.
3. The separate SpamAssassin email corpus under `data\raw\spamassassin`.

Kaggle CSVs are preferred by the trainer when both SMS files exist. The download command uses Kaggle's API and does not silently substitute the UCI file. For a verified Kaggle download, install credentials locally at `%USERPROFILE%\.kaggle\kaggle.json`, then from the project root run:

```powershell
.\.venv\Scripts\python.exe backend\ml\download_dataset.py
```

The download helper records a SHA-256 provenance marker next to the raw Kaggle CSV. Training metadata stores the selected source, its hash, and the hash of the resulting model artifact. Do not put Kaggle credentials in this repository or in chat.

## Local setup (Windows PowerShell)

From `E:\Email spam classifier`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

Download the Kaggle dataset as above if credentials are configured. Otherwise the existing UCI TSV remains usable, but training metadata will identify that source honestly:

```powershell
.\.venv\Scripts\python.exe -m backend.ml.train
```

Start the API in one terminal:

```powershell
Set-Location "E:\Email spam classifier\backend"
& "..\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8003
```

Start the frontend in another terminal:

```powershell
Set-Location "E:\Email spam classifier\frontend"
npm ci
npm run dev -- --host 127.0.0.1 --port 5173
```

In Vite development mode the frontend defaults to `http://127.0.0.1:8003`; set `VITE_API_BASE_URL` in the terminal if your backend uses another port. Production builds must set `VITE_API_BASE_URL` in the hosting provider; do not copy the local development URL into a production `.env`.

## API

`GET /health` is public. These routes require a valid authentication cookie:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET /api/model-info`
- `GET /api/analytics`
- `GET /api/keywords`
- `POST /api/predict`
- `POST /api/predict/batch`
- `GET /api/history` (informational; prediction history is held in frontend memory only)

## Checks

```powershell
Set-Location "E:\Email spam classifier"
.\.venv\Scripts\python.exe -m pytest backend\tests\test_backend.py -q
Set-Location "E:\Email spam classifier\frontend"
npm run build
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for GitHub, Render, and Vercel setup. Deployment remains a manual action.
