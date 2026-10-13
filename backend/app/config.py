import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = BACKEND_DIR.parent
MODELS_DIR = BACKEND_DIR / "models"
DATA_DIR = BASE_DIR / "data"

APP_NAME = os.getenv("APP_NAME", "Email Spam Classifier")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8003"))
_configured_model_path = Path(os.getenv("MODEL_PATH", str(MODELS_DIR / "spam_classifier.joblib"))).expanduser()
MODEL_PATH = (
    _configured_model_path
    if _configured_model_path.is_absolute()
    else BACKEND_DIR / _configured_model_path
).resolve()
DATASET_PATH = os.getenv("DATASET_PATH", str(DATA_DIR / "processed" / "cleaned_dataset.csv"))
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:5175,http://127.0.0.1:5175",
)
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "20"))
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "5000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip().lower()
_DEVELOPMENT_SECRET = "local-development-only-change-me"
SECRET_KEY = os.getenv("SECRET_KEY", _DEVELOPMENT_SECRET)
if ENVIRONMENT == "production":
    if SECRET_KEY == _DEVELOPMENT_SECRET:
        raise RuntimeError("Set a unique SECRET_KEY before starting in production.")
    if not os.getenv("CORS_ORIGINS", "").strip():
        raise RuntimeError("Set CORS_ORIGINS to the deployed frontend origin in production.")
AUTH_TOKEN_MINUTES = int(os.getenv("AUTH_TOKEN_MINUTES", "60"))
AUTH_COOKIE_NAME = "spam_classifier_session"
AUTH_COOKIE_SECURE = os.getenv("AUTH_COOKIE_SECURE", "true" if ENVIRONMENT == "production" else "false").lower() == "true"
AUTH_COOKIE_SAMESITE = os.getenv("AUTH_COOKIE_SAMESITE", "none" if ENVIRONMENT == "production" else "lax").lower()
if AUTH_COOKIE_SAMESITE not in {"lax", "strict", "none"}:
    raise ValueError("AUTH_COOKIE_SAMESITE must be lax, strict, or none.")
if AUTH_COOKIE_SAMESITE == "none" and not AUTH_COOKIE_SECURE:
    raise ValueError("AUTH_COOKIE_SECURE must be true when AUTH_COOKIE_SAMESITE is none.")
USER_DB_PATH = Path(os.getenv("USER_DB_PATH", str(MODELS_DIR / "users.db")))
