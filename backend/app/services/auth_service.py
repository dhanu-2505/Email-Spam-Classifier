import hashlib
import hmac
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Iterator, Optional

import jwt

from app.config import AUTH_TOKEN_MINUTES, SECRET_KEY, USER_DB_PATH

ALGORITHM = "HS256"


@contextmanager
def _connection() -> Iterator[sqlite3.Connection]:
    USER_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(USER_DB_PATH, timeout=10)
    try:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password_hash TEXT NOT NULL, created_at TEXT NOT NULL)"
        )
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _hash_password(password: str, salt: Optional[bytes] = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"{salt.hex()}:{digest.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    salt_hex, digest_hex = stored.split(":", 1)
    candidate = _hash_password(password, bytes.fromhex(salt_hex)).split(":", 1)[1]
    return hmac.compare_digest(candidate, digest_hex)


def register_user(email: str, password: str) -> bool:
    normalized = email.strip().lower()
    with _connection() as connection:
        try:
            connection.execute(
                "INSERT INTO users(email, password_hash, created_at) VALUES (?, ?, ?)",
                (normalized, _hash_password(password), datetime.now(timezone.utc).isoformat()),
            )
            return True
        except sqlite3.IntegrityError:
            return False


def authenticate_user(email: str, password: str) -> bool:
    with _connection() as connection:
        row = connection.execute(
            "SELECT password_hash FROM users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
    return bool(row and _verify_password(password, row[0]))


def create_token(email: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": email.strip().lower(), "iat": now, "exp": now + timedelta(minutes=AUTH_TOKEN_MINUTES)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_token(token: str) -> str:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    subject = payload.get("sub")
    if not subject:
        raise jwt.InvalidTokenError("Token subject is missing")
    return str(subject)
