from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User, UserRole
from app.schemas import LoginIn, MeOut, PinLoginIn, TokenOut
from app.security import create_access_token, get_current_user, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _invalid() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="That sign-in didn't match. Try again."
    )


@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn, db: AsyncSession = Depends(get_db)):
    """Staff sign-in with username and password."""
    user = await db.scalar(select(User).where(User.username == body.username))
    if user is None or not user.active or not verify_password(body.password, user.password_hash):
        raise _invalid()
    return TokenOut(access_token=create_access_token(user))


@router.post("/pin", response_model=TokenOut)
async def pin_login(body: PinLoginIn, db: AsyncSession = Depends(get_db)):
    """Student sign-in: picked from their program's roster, then a PIN."""
    user = await db.get(User, body.student_id)
    if (
        user is None
        or user.role != UserRole.student
        or not user.active
        or not verify_password(body.pin, user.password_hash)
    ):
        raise _invalid()
    return TokenOut(access_token=create_access_token(user))


@router.get("/me", response_model=MeOut)
async def me(user: User = Depends(get_current_user)):
    return MeOut(id=user.id, name=user.full_name, role=user.role)
