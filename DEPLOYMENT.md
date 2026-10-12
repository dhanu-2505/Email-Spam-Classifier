# Deployment Guide

Deployment has **not** been performed. The repository contains deployment configuration for GitHub, Render (FastAPI), and Vercel (React), but no live service URL has been provisioned or verified.

## Before publishing

1. Obtain Kaggle API credentials from the Kaggle account settings and store `kaggle.json` locally at `%USERPROFILE%\.kaggle\kaggle.json`. Never commit this file.
2. Download and train using the exact requested Kaggle source from the project root:

   ```powershell
   Set-Location "E:\Email spam classifier"
   .\.venv\Scripts\python.exe backend\ml\download_dataset.py
   .\.venv\Scripts\python.exe -m backend.ml.train
   ```

   The downloader fails explicitly if Kaggle authentication is unavailable; it does not fall back to another dataset. Confirm `backend\models\model_metadata.json` reports `"kaggle_download_verified": true` before describing the trained artifact as Kaggle-sourced. If credentials are unavailable, the current local UCI archive copy can be trained, but must be described as UCI-sourced.
3. Run the tests and build from the project root/frontend:

   ```powershell
   Set-Location "E:\Email spam classifier"
   .\.venv\Scripts\python.exe -m pytest backend\tests\test_backend.py -q
   Set-Location "E:\Email spam classifier\frontend"
   npm ci
   npm run build
   ```

## Publish the source to GitHub

Check that the deployable model and metadata are included while local data, credentials, environment files, and user databases are excluded:

```powershell
Set-Location "E:\Email spam classifier"
git status --short
git check-ignore data\raw\SMSSpamCollection.tsv backend\models\users.db frontend\.env
git check-ignore backend\models\spam_classifier.joblib backend\models\model_metadata.json
```

The model artifact and metadata are explicitly unignored because the API needs them at runtime. Review `git status` carefully and ensure no `.env`, Kaggle credentials, raw dataset, or SQLite user database is staged.

Create an empty GitHub repository in the browser, then replace the remote URL below with your own:

```powershell
Set-Location "E:\Email spam classifier"
git init
git add .
git status --short
git commit -m "Prepare spam classifier for deployment"
git branch -M main
git remote add origin https://github.com/YOUR-USER/YOUR-REPOSITORY.git
git push -u origin main
```

If this directory is already a Git repository, do not run `git init`; inspect `git status` and set the remote only if needed.

## Deploy FastAPI on Render

1. Create the Vercel project first with root directory `frontend`; its initial API setting can be a temporary value because no login/API checks are possible yet. Record the Vercel origin.
2. In Render, create a new **Blueprint** from the GitHub repository and review `render.yaml`. Supply the exact Vercel origin for the required `CORS_ORIGINS` variable when prompted.
3. Render generates `SECRET_KEY` from the blueprint. Keep `ENVIRONMENT=production`, `AUTH_COOKIE_SECURE=true`, and `AUTH_COOKIE_SAMESITE=none`.
4. The blueprint uses a persistent disk mounted at `/var/data` for the SQLite account database. This is needed so local account registration survives service restarts.
5. Check the Render health check at `/health`. It is public and confirms whether the model file loads; model and analytics routes require login.

Do not set `MODEL_PATH` to a machine-specific Windows path. The blueprint uses `models/spam_classifier.joblib`, relative to the backend service root.

## Deploy React on Vercel

1. Import the same GitHub repository into Vercel (if it has not already been created above).
2. Set the project **Root Directory** to `frontend`.
3. Set `VITE_API_BASE_URL` to the actual Render service base URL (for example `https://YOUR-SERVICE.onrender.com`, without a trailing slash). Do not use the example URL literally.
4. Build command: `npm run build`; output directory: `dist`.
5. Redeploy after setting the real API URL. `frontend\vercel.json` routes direct page requests back to the SPA entry point.

The backend must allow the exact Vercel origin in `CORS_ORIGINS`; credentials are enabled for the cross-origin secure session cookie. Browser privacy settings may still restrict third-party cookies when the frontend and backend use different site domains; verify the actual deployed login flow.

## Verify a real deployment

After both hosts report deployment success, use the actual URLs from their dashboards:

```powershell
$BackendUrl = "https://YOUR-SERVICE.onrender.com"
Invoke-RestMethod "$BackendUrl/health"
```

Then open the real Vercel URL and verify Home → Login → successful login → Dashboard, protected navigation, API-backed model info/analytics/keywords, one ham prediction, one spam prediction, and logout. Confirm an unauthenticated request to a protected route is rejected. Do not report deployment as complete until these checks pass against the public URLs.

## Local launch (Windows PowerShell)

Backend terminal:

```powershell
Set-Location "E:\Email spam classifier\backend"
& "..\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8003
```

Frontend terminal:

```powershell
Set-Location "E:\Email spam classifier\frontend"
npm ci
npm run dev -- --host 127.0.0.1 --port 5173
```

Local status and public deployment status are separate: a passing local build does not imply a live deployment.
