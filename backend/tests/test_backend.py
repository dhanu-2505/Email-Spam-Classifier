import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.services import auth_service
from app.main import app
from app.services.model_service import get_model_metadata, load_pipeline
from backend.ml.data_loader import load_dataset, validate_and_prepare_dataset


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(auth_service, "USER_DB_PATH", tmp_path / "users.db")
    with TestClient(app) as test_client:
        yield test_client


def authenticated_client(client):
    email = "test-user@example.com"
    registration = client.post(
        "/api/auth/register",
        json={"email": email, "password": "test-password-123"},
    )
    assert registration.status_code == 200
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "test-password-123"},
    )
    assert response.status_code == 200
    return client


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_protected_endpoint_requires_authentication(client):
    client.post("/api/auth/logout")
    response = client.get("/api/model-info")
    assert response.status_code == 401


def test_logout_invalidates_session(client):
    session_client = authenticated_client(client)
    assert session_client.get("/api/auth/me").status_code == 200
    assert session_client.post(
        "/api/predict",
        json={"message": "The project meeting is tomorrow at 3 PM."},
    ).status_code == 200
    assert session_client.post("/api/auth/logout").status_code == 200
    assert session_client.get("/api/auth/me").status_code == 401
    assert session_client.get("/api/model-info").status_code == 401
    assert session_client.post(
        "/api/predict",
        json={"message": "The project meeting is tomorrow at 3 PM."},
    ).status_code == 401


def test_predict_empty_message(client):
    response = authenticated_client(client).post("/api/predict", json={"message": "   "})
    assert response.status_code in {400, 422}


def test_invalid_json_request(client):
    response = authenticated_client(client).post("/api/predict", content='{"message":', headers={"Content-Type": "application/json"})
    assert response.status_code in {400, 422}


def test_model_info_endpoint(client):
    response = authenticated_client(client).get("/api/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["selected_model"] == "linear_svc"
    assert data["dataset"]["dataset_type"].startswith("SMS messages")
    assert data["evaluation"]["f1"] > 0


def test_analytics_endpoint(client):
    response = authenticated_client(client).get("/api/analytics")
    assert response.status_code == 200
    assert response.json()["selected_model"] == "linear_svc"


def test_keywords_endpoint(client):
    response = authenticated_client(client).get("/api/keywords")
    assert response.status_code == 200
    assert response.json()["keywords"]["spam_terms"]


def test_real_ham_prediction(client):
    response = authenticated_client(client).post("/api/predict", json={"message": "The project meeting is tomorrow at 3 PM. Please bring the updated deck."})
    assert response.status_code == 200
    assert response.json()["label"] == "ham"


def test_real_spam_prediction(client):
    response = authenticated_client(client).post("/api/predict", json={"message": "URGENT! You won a free prize. Click now to claim your reward."})
    assert response.status_code == 200
    assert response.json()["label"] == "spam"


def test_oversized_message(client):
    response = authenticated_client(client).post("/api/predict", json={"message": "x" * 5001})
    assert response.status_code in {413, 422}


def test_cors_for_local_frontend(client):
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


def test_registration_hashes_password_and_login_persists_across_connections(client, tmp_path):
    email = "New.User@example.com"
    password = "secure-test-password"
    registration = client.post(
        "/api/auth/register",
        json={"email": email, "password": password},
    )
    assert registration.status_code == 200
    assert registration.json()["message"] == "Account created. You can now log in."

    with sqlite3.connect(tmp_path / "users.db") as connection:
        stored_email, stored_hash = connection.execute(
            "SELECT email, password_hash FROM users"
        ).fetchone()
    assert stored_email == "new.user@example.com"
    assert stored_hash != password
    assert ":" in stored_hash

    login = client.post(
        "/api/auth/login",
        json={"email": "  NEW.USER@EXAMPLE.COM ", "password": password},
    )
    assert login.status_code == 200
    assert login.json() == {"authenticated": True, "email": "new.user@example.com"}
    assert "httponly" in login.headers["set-cookie"].lower()
    assert client.get("/api/auth/me").json() == {
        "authenticated": True,
        "email": "new.user@example.com",
    }
    assert client.get("/api/model-info").status_code == 200


def test_login_session_survives_client_refresh_and_allows_classifier(client):
    authenticated_client(client)
    with TestClient(app, cookies=client.cookies) as refreshed_client:
        assert refreshed_client.get("/api/auth/me").status_code == 200
        prediction = refreshed_client.post(
            "/api/predict",
            json={"message": "The project meeting is tomorrow at 3 PM."},
        )
    assert prediction.status_code == 200
    assert prediction.json()["label"] == "ham"


def test_classifier_requires_authenticated_session(client):
    response = client.post(
        "/api/predict",
        json={"message": "The project meeting is tomorrow at 3 PM."},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required."


def test_registration_rejects_duplicate_email_case_insensitively(client):
    payload = {"email": "duplicate@example.com", "password": "secure-test-password"}
    assert client.post("/api/auth/register", json=payload).status_code == 200
    duplicate = client.post(
        "/api/auth/register",
        json={"email": "DUPLICATE@example.com", "password": "another-password"},
    )
    assert duplicate.status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "not-an-email", "password": "secure-test-password"},
        {"email": "person@example.com", "password": "short"},
    ],
)
def test_registration_rejects_invalid_input_without_creating_account(client, tmp_path, payload):
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422
    assert all("input" not in error for error in response.json()["detail"])
    with sqlite3.connect(tmp_path / "users.db") as connection:
        table = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='users'"
        ).fetchone()
    assert table is None


def test_login_rejects_invalid_credentials(client):
    payload = {"email": "login@example.com", "password": "secure-test-password"}
    assert client.post("/api/auth/register", json=payload).status_code == 200

    wrong_password = client.post(
        "/api/auth/login",
        json={"email": payload["email"], "password": "wrong-password"},
    )
    unknown_account = client.post(
        "/api/auth/login",
        json={"email": "missing@example.com", "password": payload["password"]},
    )
    assert wrong_password.status_code == 401
    assert unknown_account.status_code == 401
    assert client.get("/api/auth/me").status_code == 401


def test_auth_database_is_persistent_at_configured_path(monkeypatch, tmp_path):
    database_path = tmp_path / "persistent" / "users.db"
    monkeypatch.setattr(auth_service, "USER_DB_PATH", database_path)

    assert auth_service.register_user("durable@example.com", "secure-test-password")
    assert database_path.is_file()
    assert auth_service.authenticate_user("durable@example.com", "secure-test-password")
