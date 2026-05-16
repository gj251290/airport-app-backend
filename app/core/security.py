import os
import hashlib
from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.database.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES_DEFAULT = 60


def get_access_token_expire_minutes() -> int:
    raw_value = os.getenv(
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", str(JWT_EXPIRE_MINUTES_DEFAULT)
    )
    try:
        expire_minutes = int(raw_value)
    except ValueError:
        expire_minutes = JWT_EXPIRE_MINUTES_DEFAULT

    if expire_minutes <= 0:
        return JWT_EXPIRE_MINUTES_DEFAULT
    return expire_minutes


def _get_jwt_secret_key() -> str:
    secret = os.getenv("JWT_SECRET_KEY")
    if not secret:
        raise RuntimeError(
            "JWT_SECRET_KEY no esta configurada. Define esta variable en tu archivo .env"
        )
    return secret


def _normalize_password(plain_password: str) -> bytes:
    data = plain_password.encode("utf-8")
    if len(data) > 72:
        # bcrypt max password length; pre-hash for safety.
        data = hashlib.sha256(data).digest()
    return data


def hash_password(plain_password: str) -> str:
    if not plain_password:
        return ""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(_normalize_password(plain_password), salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    if not plain_password or not password_hash:
        return False
    try:
        return bcrypt.checkpw(
            _normalize_password(plain_password), password_hash.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(subject: str, role: str) -> str:
    expire_minutes = get_access_token_expire_minutes()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=expire_minutes),
    }
    return jwt.encode(payload, _get_jwt_secret_key(), algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, _get_jwt_secret_key(), algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        raise UnauthorizedError("Missing bearer token")

    payload = decode_access_token(token)
    subject = payload.get("sub")

    if not subject:
        raise UnauthorizedError("Token payload is invalid")

    try:
        user_id = UUID(str(subject))
    except ValueError as exc:
        raise UnauthorizedError("Token payload is invalid") from exc

    user = await db.get(User, user_id)
    if not user:
        raise UnauthorizedError("User not found for token")

    return user
