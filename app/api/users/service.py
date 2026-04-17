import logging
import uuid

from app.core.security.hashing import hash_password
from app.mock import db

logger = logging.getLogger(__name__)


def get_user_by_email(email: str) -> dict[str, str] | None:
    return db.users.get(email)


def create_user(username: str, email: str, password: str) -> dict[str, str]:
    user_id = str(uuid.uuid4())
    hashed = hash_password(password)
    user: dict[str, str] = {
        "id": user_id,
        "username": username,
        "email": email,
        "hashed_password": hashed,
    }
    db.users[email] = user
    masked = email[:2] + "***" + email[email.index("@") :]
    logger.info("User created: %s", masked)
    return user
