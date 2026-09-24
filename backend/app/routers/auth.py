from fastapi import APIRouter, Depends

from app.config import get_settings
from app.models import User
from app.schemas import MeOut
from app.security import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=MeOut)
async def me(user: User = Depends(get_current_user)):
    """Who Authelia says is signed in. Sign-in itself happens in Authelia."""
    return MeOut(
        id=user.id,
        name=user.display_name,
        role=user.role,
        logout_url=get_settings().AUTHELIA_LOGOUT_URL,
    )
