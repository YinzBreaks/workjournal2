from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.dependencies import get_current_user, get_db
from app.models.base import User
from app.services.auth import (
    blacklist_refresh_token,
    create_token_pair,
    log_audit,
    verify_pin,
    verify_refresh_token,
)
from app.services.oidc import (
    build_authorization_url,
    exchange_code_for_tokens,
    generate_state_nonce,
    sign_state_cookie,
    validate_id_token,
    verify_state_cookie,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# --- Schemas ---


class PinLoginRequest(BaseModel):
    program_id: str
    user_id: str
    pin: str


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# --- OIDC (Teacher) ---


@router.get("/oidc/login")
async def oidc_login(response: Response):
    state, nonce = generate_state_nonce()
    cookie_value = sign_state_cookie(state, nonce)

    authorization_url = build_authorization_url(state, nonce)

    response = Response(
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        headers={"Location": authorization_url},
    )
    response.set_cookie(
        key="oidc_state",
        value=cookie_value,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=600,
    )
    return response


@router.get("/oidc/callback")
async def oidc_callback(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    ip = request.client.host if request.client else None
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")

    if error:
        await log_audit(db, "oidc_callback_error", ip_address=ip, details=error)
        raise HTTPException(status_code=400, detail=f"OIDC error: {error}")

    if not code or not state:
        await log_audit(
            db, "oidc_callback_missing_params", ip_address=ip
        )
        raise HTTPException(status_code=400, detail="Missing code or state")

    cookie_value = request.cookies.get("oidc_state")
    if not cookie_value:
        await log_audit(db, "oidc_callback_missing_cookie", ip_address=ip)
        raise HTTPException(status_code=400, detail="Missing state cookie")

    try:
        cookie_data = verify_state_cookie(cookie_value)
    except Exception:
        await log_audit(db, "oidc_callback_invalid_cookie", ip_address=ip)
        raise HTTPException(status_code=400, detail="Invalid state cookie")

    if cookie_data["state"] != state:
        await log_audit(db, "oidc_callback_state_mismatch", ip_address=ip)
        raise HTTPException(status_code=400, detail="State mismatch")

    try:
        token_data = await exchange_code_for_tokens(code)
    except Exception:
        await log_audit(db, "oidc_token_exchange_failed", ip_address=ip)
        raise HTTPException(status_code=502, detail="Token exchange failed")

    id_token = token_data.get("id_token")
    if not id_token:
        await log_audit(db, "oidc_no_id_token", ip_address=ip)
        raise HTTPException(status_code=502, detail="No id_token in response")

    try:
        id_claims = await validate_id_token(id_token, cookie_data["nonce"])
    except Exception as e:
        await log_audit(
            db, "oidc_id_token_invalid", ip_address=ip, details=str(e)
        )
        raise HTTPException(status_code=401, detail="Invalid id_token")

    entra_oid = id_claims.get("oid") or id_claims.get("sub")
    email = id_claims.get("email") or id_claims.get("preferred_username")
    display_name = id_claims.get("name", email or "Unknown")

    result = await db.execute(select(User).where(User.entra_oid == entra_oid))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            email=email,
            display_name=display_name,
            role="teacher",
            entra_oid=entra_oid,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        await log_audit(
            db, "teacher_provisioned", user_id=user.id, ip_address=ip
        )

    tokens = create_token_pair(user.id, user.role, user.email)
    await log_audit(db, "oidc_login_success", user_id=user.id, ip_address=ip)

    response = Response(
        status_code=200,
        content=TokenResponse(**tokens).model_dump_json(),
        media_type="application/json",
    )
    response.delete_cookie("oidc_state")
    return response


# --- PIN (Student) ---


@router.post("/pin", response_model=TokenResponse)
async def pin_login(
    body: PinLoginRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    ip = request.client.host if request.client else None

    result = await db.execute(
        select(User).where(
            User.id == body.user_id,
            User.program_id == body.program_id,
            User.role == "student",
        )
    )
    user = result.scalar_one_or_none()

    if user is None or user.pin_hash is None:
        await log_audit(
            db,
            "pin_login_user_not_found",
            ip_address=ip,
            details=f"program={body.program_id} user={body.user_id}",
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_pin(body.pin, user.pin_hash):
        await log_audit(
            db, "pin_login_failed", user_id=user.id, ip_address=ip
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")

    tokens = create_token_pair(user.id, user.role)
    await log_audit(db, "pin_login_success", user_id=user.id, ip_address=ip)
    return tokens


# --- Admin ---


@router.post("/admin", response_model=TokenResponse)
async def admin_login(
    body: AdminLoginRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    ip = request.client.host if request.client else None
    settings = get_settings()

    if body.username != settings.ADMIN_USER or body.password != settings.ADMIN_PASS:
        await log_audit(
            db,
            "admin_login_failed",
            ip_address=ip,
            details=f"username={body.username}",
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")

    result = await db.execute(
        select(User).where(User.email == settings.ADMIN_USER, User.role == "admin")
    )
    admin_user = result.scalar_one_or_none()

    if admin_user is None:
        admin_user = User(
            email=settings.ADMIN_USER,
            display_name="Admin",
            role="admin",
        )
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)

    tokens = create_token_pair(admin_user.id, admin_user.role, admin_user.email)
    await log_audit(
        db, "admin_login_success", user_id=admin_user.id, ip_address=ip
    )
    return tokens


# --- Refresh ---


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    ip = request.client.host if request.client else None

    payload = await verify_refresh_token(body.refresh_token, db)
    if payload is None:
        await log_audit(db, "refresh_failed", ip_address=ip)
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    await blacklist_refresh_token(body.refresh_token, db)

    tokens = create_token_pair(payload["sub"], payload["role"])
    await log_audit(db, "token_refreshed", user_id=payload["sub"], ip_address=ip)
    return tokens


# --- Logout ---


@router.post("/logout")
async def logout(
    body: LogoutRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    ip = request.client.host if request.client else None

    success = await blacklist_refresh_token(body.refresh_token, db)
    if success:
        await log_audit(db, "logout_success", ip_address=ip)
    else:
        await log_audit(db, "logout_invalid_token", ip_address=ip)

    return {"detail": "Logged out"}
