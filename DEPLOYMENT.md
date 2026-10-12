# Deployment Guide

The source is published at [dhanu-2505/Email-Spam-Classifier](https://github.com/dhanu-2505/Email-Spam-Classifier). Verified production origins are [Vercel](https://email-spam-classifier-three.vercel.app/) and [Render](https://email-spam-classifier-htyy.onrender.com/). Commit `a8a35c6` is pushed to GitHub, and the Vercel same-origin `/api` rewrite is live. Production registration/login and cookie-backed protected access were exercised successfully. However, `/health` currently reports `model_loaded: false`, so an authenticated `/api/predict` returns `503 Model is not available; retraining is required.` Production classification is not verified working. The checked-in model is identified as an extracted UCI SMS archive copy, not a verified Kaggle API download.

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

## GitHub source status and future updates

The repository and `origin` remote already exist; do not run `git init` or replace the remote. For these authentication changes, review the files and confirm that local data, credentials, environment files, and user databases are excluded:

```powershell
Set-Location "E:\Email spam classifier"
git status --short
git check-ignore data\raw\SMSSpamCollection.tsv backend\models\users.db frontend\.env
git check-ignore backend\models\spam_classifier.joblib backend\models\model_metadata.json
git remote -v
```

The model artifact and metadata are explicitly allowed because the API needs them at runtime. The ignore check for those two files should therefore report that they are **not** ignored. Review `git status` carefully and ensure no `.env`, Kaggle credentials, raw dataset, or SQLite user database is staged. After reviewing intended changes, publish them with:

```powershell
Set-Location "E:\Email spam classifier"
git add -A
git status --short
git commit -m "Describe the change"
git push origin main
```

`git add -A` stages all non-ignored changes, including the deployable model if it changes. Inspect the staged file list before committing; never stage `.env` files, Kaggle credentials, local datasets, or account databases.

## Deploy FastAPI on Render

1. In Vercel, import the GitHub repository and set the project root directory to `frontend`. This initial setup is only to obtain the assigned frontend origin; do not deploy yet. Record that exact origin (scheme and host, no trailing slash).
2. In Render, create a new **Blueprint** from the GitHub repository and review `render.yaml`. Supply the exact Vercel origin for the required `CORS_ORIGINS` variable when prompted.
3. Render generates `SECRET_KEY` from the blueprint. Keep `ENVIRONMENT=production`, `AUTH_COOKIE_SECURE=true`, and `AUTH_COOKIE_SAMESITE=none`.
4. The blueprint uses a persistent disk mounted at `/var/data` for the SQLite account database. This is needed so local account registration survives service restarts.
5. Check the Render health check at `/health`. It is public and confirms whether the model file loads; model and analytics routes require login.

After pushing the model-loading fix, open the Render dashboard and choose **Manual Deploy → Deploy latest commit** for `main`. Then verify:

```powershell
Invoke-RestMethod "https://email-spam-classifier-htyy.onrender.com/health"
```

The model artifact and metadata are tracked in Git, and the required `scikit-learn` and `joblib` dependencies are in `backend\requirements.txt`. Relative `MODEL_PATH` values are resolved from the `backend` directory, independent of Render's process working directory. On startup the backend logs the absolute path and artifact size when loading succeeds; if it fails, Render logs an error with the path and exception type/message, without logging secrets. If health still reports `"model_loaded": false`, inspect the Render startup log for that model-loading message and check the effective `MODEL_PATH` environment setting. Do not claim production classification works unless health reports `"model_loaded": true`.

Do not set `MODEL_PATH` to a machine-specific Windows path. The blueprint uses `models/spam_classifier.joblib`, relative to the backend service root.

## Deploy React on Vercel

1. Set the project **Root Directory** to `frontend`.
2. Build command: `npm run build`; output directory: `dist`.
3. Deploy. `frontend\vercel.json` sends `/api/*` through a same-origin rewrite to the Render API and routes other direct page requests back to the SPA entry point. Keep the rewrite destination synchronized with the actual Render URL. Do not set production `VITE_API_BASE_URL`; the browser must call the same Vercel origin so the session cookie is first-party.

After Vercel assigns the final production origin, update Render's `CORS_ORIGINS` to exactly that origin and redeploy the backend. Local development may call Render directly, but production browser requests go through Vercel's same-origin rewrite so browser privacy settings do not need to allow third-party cookies.

### Account storage and login troubleshooting

- Keep Render's `USER_DB_PATH` set to `/var/data/users.db` and the persistent disk mounted at `/var/data`. Do not point account storage at the service's temporary filesystem, where accounts may disappear on replacement or restart.
- Production API requests use a same-origin Vercel rewrite to avoid depending on third-party cookies. If the Render hostname changes, update the rewrite destination in `frontend\vercel.json` and redeploy Vercel. Keep the browser API base relative; do not override it with a cross-site Render URL.
- Check the Render service's deployed commit and environment settings before diagnosing a live login. These local changes do not affect production until that code is deployed.
- In browser developer tools, inspect request URLs, HTTP status, and response details only. Production auth requests should use the Vercel origin and `/api/...` path. Registration should return `200`; duplicate email returns `409`; malformed input returns `422` without echoing submitted field values; matching login returns `200` with a session cookie, while unknown email or a wrong password returns the same generic `401`. Never share request bodies, passwords, or cookie/token values.
- Registration creates the account but does not automatically sign the user in. It redirects to Login with a confirmation; sign in using the same email and password. Verify `/api/auth/me` succeeds after login and protected APIs return `401` after logout.

## Verify a real deployment

After both hosts report deployment success, use the actual URLs from their dashboards:

```powershell
$BackendUrl = "https://YOUR-SERVICE.onrender.com"
Invoke-RestMethod "$BackendUrl/health"
```

Then open the real Vercel URL and verify Home → Login → successful login → Dashboard, protected navigation, API-backed model info/analytics/keywords, one ham prediction, one spam prediction, and logout. Confirm an unauthenticated request to a protected route is rejected. Do not report deployment as complete until these checks pass against the public URLs.

After pushing changes, confirm both hosts deployed the new GitHub commit (or manually trigger production redeployment if automatic deployments are disabled) before repeating the checks.

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

To run the backend tests and verify model startup locally:

```powershell
Set-Location "E:\Email spam classifier"
.\.venv\Scripts\python.exe -m pytest backend\tests\test_backend.py -q
Set-Location "E:\Email spam classifier\backend"
& "..\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8004
```

The startup log should say `Loaded spam classification model from ...\backend\models\spam_classifier.joblib`. In another PowerShell window, verify:

```powershell
Invoke-RestMethod "http://127.0.0.1:8004/health"
```

Expected local result with the checked-in artifact: `model_loaded` is `true`. Stop the local server with `Ctrl+C`.

Local status and public deployment status are separate: a passing local build does not imply a live deployment.
