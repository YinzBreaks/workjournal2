from datetime import datetime, timedelta, timezone
from hashlib import sha256

import bcrypt
from jose import jwt as jose_jwt
from jose.exceptions import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.audit import AuditLog
from app.models.token import RefreshToken
from app.models.user import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user_id: int, role: str, name: str = "", email: str | None = None) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "user_id": user_id,
        "role": role,
        "name": name,
        "email": email,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jose_jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int, role: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "user_id": user_id,
        "role": role,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jose_jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_token_pair(user: User) -> dict:
    name = f"{user.first_name} {user.last_name}".strip()
    return {
        "access_token": create_access_token(user.id, user.role.value, name, user.email),
        "refresh_token": create_refresh_token(user.id, user.role.value),
        "token_type": "bearer",
    }


async def verify_access_token(token: str, db: AsyncSession) -> dict | None:
    settings = get_settings()
    try:
        payload = jose_jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


async def verify_refresh_token(token: str, db: AsyncSession) -> dict | None:
    settings = get_settings()
    try:
        payload = jose_jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "refresh":
            return None

        token_hash = sha256(token.encode()).hexdigest()
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked == True,
            )
        )
        if result.scalar_one_or_none() is not None:
            return None

        return payload
    except JWTError:
        return None


async def revoke_refresh_token(token: str, db: AsyncSession) -> bool:
    settings = get_settings()
    try:
        payload = jose_jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_hash = sha256(token.encode()).hexdigest()
        user_id = payload.get("user_id")
        exp = payload.get("exp")

        entry = RefreshToken(
            token_hash=token_hash,
            user_id=user_id,
            expires_at=datetime.fromtimestamp(exp, tz=timezone.utc) if exp else datetime.now(timezone.utc),
            revoked=True,
        )
        db.add(entry)
        await db.commit()
        return True
    except JWTError:
        return False


async def log_audit(
    db: AsyncSession,
    action: str,
    user_id: int | None = None,
    ip_address: str | None = None,
    extra: dict | None = None,
) -> None:
    entry = AuditLog(
        action=action,
        user_id=user_id,
        ip_address=ip_address,
        extra=extra,
    )
    db.add(entry)
    await db.commit()
