import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError

from app.mock import db
from app.security.hashing import verify_password
from app.security.jwt import create_access_token, create_refresh_token, decode_token

logger = logging.getLogger(__name__)

BRUTE_FORCE_MAX_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


def _get_brute_force_record(ip: str) -> dict[str, int | datetime | None]:
    if ip not in db.brute_force:
        db.brute_force[ip] = {"failed_attempts": 0, "locked_until": None}
    return db.brute_force[ip]


def check_ip_locked(ip: str) -> datetime | None:
    """Returns locked_until datetime if IP is locked, else None."""
    record = _get_brute_force_record(ip)
    locked_until = record.get("locked_until")
    if locked_until is not None and isinstance(locked_until, datetime):
        if datetime.now(UTC) < locked_until:
            return locked_until
        else:
            # Lock expired, reset
            record["locked_until"] = None
            record["failed_attempts"] = 0
    return None


def _increment_failed_attempts(ip: str) -> None:
    record = _get_brute_force_record(ip)
    attempts = record.get("failed_attempts")
    if not isinstance(attempts, int):
        attempts = 0
    attempts += 1
    record["failed_attempts"] = attempts
    if attempts >= BRUTE_FORCE_MAX_ATTEMPTS:
        locked_until = datetime.now(UTC) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        record["locked_until"] = locked_until
        masked_ip = ip[:4] + "***"
        logger.warning("IP locked due to brute force: %s, until: %s", masked_ip, locked_until.isoformat())


def login(email: str, password: str, ip: str) -> dict[str, str] | None:
    """
    Attempt to authenticate a user.
    Returns token dict on success, None on failure.
    Caller should raise 401 on None.
    """
    masked_email = email[:2] + "***" + email[email.index("@") :]

    # Check brute force
    locked_until = check_ip_locked(ip)
    if locked_until is not None:
        return None  # caller will check and return 423

    # Look up user
    user = db.users.get(email)
    if user is None:
        logger.info("Login failed (user not found): %s from %s", masked_email, ip)
        _increment_failed_attempts(ip)
        return None

    # Verify password
    hashed = user.get("hashed_password", "")
    if not verify_password(password, hashed):
        logger.info("Login failed (wrong password): %s from %s", masked_email, ip)
        _increment_failed_attempts(ip)
        return None

    # Success — reset failed attempts
    record = _get_brute_force_record(ip)
    record["failed_attempts"] = 0
    record["locked_until"] = None

    user_id = user["id"]
    refresh_token, jti = create_refresh_token(user_id, ip)
    access_token = create_access_token(user_id, ip, jti)

    # Store jti in allowlist
    db.refresh_tokens[jti] = user_id

    logger.info("Login successful: %s from %s", masked_email, ip)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh(refresh_token_str: str, ip: str) -> dict[str, str] | None:
    """
    Attempt to refresh tokens using a refresh token.
    Returns new token dict on success, None on failure (invalid/expired/reused).
    """
    try:
        payload: dict[str, Any] = decode_token(refresh_token_str)
    except JWTError:
        return None

    if payload.get("type") != "refresh":
        return None

    jti = payload.get("jti")
    if not isinstance(jti, str):
        return None

    # Check allowlist
    if jti not in db.refresh_tokens:
        return None

    # Check IP
    token_ip = payload.get("ip")
    if token_ip != ip:
        return None

    user_id = payload.get("sub")
    if not isinstance(user_id, str):
        return None

    # Invalidate old token
    del db.refresh_tokens[jti]

    # Issue new tokens
    new_refresh_token, new_jti = create_refresh_token(user_id, ip)
    new_access_token = create_access_token(user_id, ip, new_jti)
    db.refresh_tokens[new_jti] = user_id

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


def logout(access_token_str: str, ip: str) -> bool:
    """
    Invalidate session by removing refresh token from allowlist.
    Returns True on success, False on invalid token.
    """
    try:
        payload: dict[str, Any] = decode_token(access_token_str)
    except JWTError:
        return False

    if payload.get("type") != "access":
        return False

    token_ip = payload.get("ip")
    if token_ip != ip:
        return False

    jti = payload.get("jti")
    if not isinstance(jti, str):
        return False

    # Remove from allowlist (jti in access token = refresh token jti)
    db.refresh_tokens.pop(jti, None)

    return True
