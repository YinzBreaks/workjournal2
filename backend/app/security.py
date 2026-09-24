"""Passwords, access tokens, and the "who is calling" dependencies."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_db
from app.models import ProgramStaff, Staff, User, UserRole

ALGORITHM = "HS256"
bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash:
        return False
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user: User) -> str:
    settings = get_settings()
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user.id), "role": user.role.value, "exp": expires}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Your session has ended. Sign in again."
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise _unauthorized()
    try:
        payload = jwt.decode(
            credentials.credentials, get_settings().SECRET_KEY, algorithms=[ALGORITHM]
        )
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise _unauthorized()

    # Looked up every request so deactivating a user signs them out.
    user = await db.get(User, user_id)
    if user is None or not user.active:
        raise _unauthorized()
    return user


def require_role(*roles: UserRole):
    async def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this.",
            )
        return user

    return checker


async def ensure_program_access(db: AsyncSession, user: User, program_id: int) -> None:
    """Admins see every program; teachers only the ones they're staff on."""
    if user.role == UserRole.admin:
        return
    if user.role == UserRole.teacher:
        link = await db.scalar(
            select(ProgramStaff)
            .join(Staff, Staff.id == ProgramStaff.staff_id)
            .where(ProgramStaff.program_id == program_id, Staff.user_id == user.id)
        )
        if link is not None:
            return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have access to this program.",
    )
