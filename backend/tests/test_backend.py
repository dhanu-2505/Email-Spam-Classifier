from fastapi.testclient import TestClient

from app.main import app
from app.services.model_service import get_model_metadata, load_pipeline
from backend.ml.data_loader import load_dataset, validate_and_prepare_dataset

client = TestClient(app)


def authenticated_client():
    email = "test-user@example.com"
    client.post("/api/auth/register", json={"email": email, "password": "test-password-123"})
    response = client.post("/api/auth/login", json={"email": email, "password": "test-password-123"})
    assert response.status_code == 200
    return client


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_protected_endpoint_requires_authentication():
    client.post("/api/auth/logout")
    response = client.get("/api/model-info")
    assert response.status_code == 401


def test_logout_invalidates_session():
    session_client = authenticated_client()
    assert session_client.get("/api/auth/me").status_code == 200
    assert session_client.post("/api/auth/logout").status_code == 200
    assert session_client.get("/api/auth/me").status_code == 401
    assert session_client.get("/api/model-info").status_code == 401


def test_predict_empty_message():
    response = authenticated_client().post("/api/predict", json={"message": "   "})
    assert response.status_code in {400, 422}


def test_invalid_json_request():
    response = authenticated_client().post("/api/predict", content='{"message":', headers={"Content-Type": "application/json"})
    assert response.status_code in {400, 422}


def test_model_info_endpoint():
    response = authenticated_client().get("/api/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["selected_model"] == "linear_svc"
    assert data["dataset"]["dataset_type"].startswith("SMS messages")
    assert data["evaluation"]["f1"] > 0


def test_analytics_endpoint():
    response = authenticated_client().get("/api/analytics")
    assert response.status_code == 200
    assert response.json()["selected_model"] == "linear_svc"


def test_keywords_endpoint():
    response = authenticated_client().get("/api/keywords")
    assert response.status_code == 200
    assert response.json()["keywords"]["spam_terms"]


def test_real_ham_prediction():
    response = authenticated_client().post("/api/predict", json={"message": "The project meeting is tomorrow at 3 PM. Please bring the updated deck."})
    assert response.status_code == 200
    assert response.json()["label"] == "ham"


def test_real_spam_prediction():
    response = authenticated_client().post("/api/predict", json={"message": "URGENT! You won a free prize. Click now to claim your reward."})
    assert response.status_code == 200
    assert response.json()["label"] == "spam"


def test_oversized_message():
    response = client.post("/api/predict", json={"message": "x" * 5001})
    assert response.status_code in {413, 422}


def test_cors_for_local_frontend():
    response = client.get("/health", headers={"Origin": "http://127.0.0.1:5174"})
    assert response.headers.get("access-control-allow-origin") == "http://127.0.0.1:5174"
    preview_response = client.get("/health", headers={"Origin": "http://127.0.0.1:5175"})
    assert preview_response.headers.get("access-control-allow-origin") == "http://127.0.0.1:5175"


def test_model_artifact_matches_metadata():
    metadata = get_model_metadata()
    pipeline = load_pipeline()
    assert pipeline is not None
    assert type(pipeline.named_steps["classifier"]).__name__ == "LinearSVC"
    assert metadata["selected_model"] == "linear_svc"
    assert metadata["model_artifact_sha256"]


def test_kaggle_sms_csv_format(tmp_path):
    dataset_path = tmp_path / "spam.csv"
    dataset_path.write_text(
        "v1,v2,Unnamed: 2\nham,Hello there,\nspam,Claim your prize,\n",
        encoding="utf-8",
    )
    prepared = validate_and_prepare_dataset(load_dataset(str(dataset_path)))
    assert prepared["label"].tolist() == ["ham", "spam"]
    assert prepared["text"].tolist() == ["Hello there", "Claim your prize"]
