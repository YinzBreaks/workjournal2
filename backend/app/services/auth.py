from datetime import datetime, timedelta, timezone
from uuid import uuid4

import bcrypt
from jose import jwt as jose_jwt
from jose.exceptions import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.base import AuditLog, RefreshTokenBlacklist, User


def hash_pin(pin: str) -> str:
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()


def verify_pin(pin: str, pin_hash: str) -> bool:
    return bcrypt.checkpw(pin.encode(), pin_hash.encode())


def create_access_token(user_id: str, role: str, email: str | None = None) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "role": role,
        "email": email,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jose_jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str, role: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "role": role,
        "type": "refresh",
        "jti": str(uuid4()),
        "iat": now,
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jose_jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_token_pair(user_id: str, role: str, email: str | None = None) -> dict:
    return {
        "access_token": create_access_token(user_id, role, email),
        "refresh_token": create_refresh_token(user_id, role),
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

        jti = payload.get("jti")
        result = await db.execute(
            select(RefreshTokenBlacklist).where(RefreshTokenBlacklist.jti == jti)
        )
        if result.scalar_one_or_none() is not None:
            return None

        return payload
    except JWTError:
        return None


async def blacklist_refresh_token(token: str, db: AsyncSession) -> bool:
    settings = get_settings()
    try:
        payload = jose_jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        jti = payload.get("jti")
        if not jti:
            return False

        entry = RefreshTokenBlacklist(jti=jti)
        db.add(entry)
        await db.commit()
        return True
    except JWTError:
        return False


async def log_audit(
    db: AsyncSession,
    action: str,
    user_id: str | None = None,
    ip_address: str | None = None,
    details: str | None = None,
) -> None:
    entry = AuditLog(
        action=action,
        user_id=user_id,
        ip_address=ip_address,
        details=details,
    )
    db.add(entry)
    await db.commit()
