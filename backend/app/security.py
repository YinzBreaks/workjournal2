"""Who is calling, and what they're allowed to touch.

Identity comes ONLY from the headers Caddy injects after Authelia forward
auth (same contract as beattieNetTrack's src/lib/auth.ts). Caddy strips any
client-supplied copies of these headers at the edge, and this container is
only reachable on the internal `beattie` Docker network, never published.
Never read a user id or role from a request body, query, or path.
"""

from dataclasses import dataclass

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.errors import account_disabled, forbidden, not_signed_in
from app.models import ProgramStaff, Staff, User, UserRole
from app.provisioning import sync_user


@dataclass(frozen=True)
class Identity:
    username: str
    name: str
    email: str
    groups: frozenset[str]

    @property
    def role(self) -> UserRole:
        if "admins" in self.groups:
            return UserRole.admin
        if "teachers" in self.groups:
            return UserRole.teacher
        return UserRole.student


def _header(request: Request, name: str) -> str:
    return (
        request.headers.get(f"remote-{name}")
        or request.headers.get(f"x-forwarded-{name}")
        or ""
    ).strip()


def read_identity(request: Request) -> Identity | None:
    username = _header(request, "user")
    if not username:
        return None
    groups = frozenset(
        g.strip().lower() for g in _header(request, "groups").split(",") if g.strip()
    )
    return Identity(
        username=username,
        name=_header(request, "name") or username[:1].upper() + username[1:],
        email=_header(request, "email") or f"{username}@beattietech.local",
        groups=groups,
    )


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    identity = read_identity(request)
    if identity is None:
        raise not_signed_in()
    user = await sync_user(db, identity)
    if not user.active:
        raise account_disabled()
    return user


def require_role(*roles: UserRole):
    async def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise forbidden()
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
    raise forbidden()
