import hashlib
import hmac
import os

from src.database import get_session, User


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, 200_000
    )
    return salt.hex() + ":" + digest.hex()


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split(":")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt, 200_000
        )
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def ensure_default_admin():
    db = get_session()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if user is None:
            db.add(User(
                username="admin",
                password_hash=hash_password("admin123"),
                role="admin"
            ))
            db.commit()
    finally:
        db.close()


def authenticate(username, password):
    db = get_session()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user and verify_password(password, user.password_hash):
            return {
                "id": user.id,
                "username": user.username,
                "role": user.role,
            }
        return None
    finally:
        db.close()
