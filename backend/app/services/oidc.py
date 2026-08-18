import hashlib
import secrets
from urllib.parse import urlencode

import httpx
from jose import jwt as jose_jwt
from jose.exceptions import JWTError

from app.config import get_settings

_jwks_cache: dict | None = None


async def get_openid_config() -> dict:
    settings = get_settings()
    url = (
        f"https://login.microsoftonline.com/{settings.ENTRA_TENANT_ID}"
        f"/v2.0/.well-known/openid-configuration"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


async def get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache
    config = await get_openid_config()
    async with httpx.AsyncClient() as client:
        resp = await client.get(config["jwks_uri"])
        resp.raise_for_status()
        _jwks_cache = resp.json()
        return _jwks_cache


def generate_state_nonce() -> tuple[str, str]:
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    return state, nonce


def build_authorization_url(state: str, nonce: str) -> str:
    settings = get_settings()
    config_url = (
        f"https://login.microsoftonline.com/{settings.ENTRA_TENANT_ID}"
        f"/oauth2/v2.0/authorize"
    )
    params = {
        "client_id": settings.ENTRA_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.ENTRA_REDIRECT_URI,
        "scope": "openid profile email",
        "state": state,
        "nonce": nonce,
        "response_mode": "query",
    }
    return f"{config_url}?{urlencode(params)}"


async def exchange_code_for_tokens(code: str) -> dict:
    settings = get_settings()
    token_url = (
        f"https://login.microsoftonline.com/{settings.ENTRA_TENANT_ID}"
        f"/oauth2/v2.0/token"
    )
    data = {
        "client_id": settings.ENTRA_CLIENT_ID,
        "client_secret": settings.ENTRA_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.ENTRA_REDIRECT_URI,
        "grant_type": "authorization_code",
        "scope": "openid profile email",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=data)
        resp.raise_for_status()
        return resp.json()


async def validate_id_token(id_token: str, expected_nonce: str) -> dict:
    settings = get_settings()
    jwks = await get_jwks()

    header = jose_jwt.get_unverified_header(id_token)
    kid = header.get("kid")

    rsa_key = None
    for key in jwks.get("keys", []):
        if key["kid"] == kid:
            rsa_key = key
            break

    if rsa_key is None:
        raise ValueError("No matching JWK found for token kid")

    payload = jose_jwt.decode(
        id_token,
        rsa_key,
        algorithms=["RS256"],
        audience=settings.ENTRA_CLIENT_ID,
        issuer=f"https://login.microsoftonline.com/{settings.ENTRA_TENANT_ID}/v2.0",
    )

    if payload.get("nonce") != expected_nonce:
        raise ValueError("Nonce mismatch")

    return payload


def sign_state_cookie(state: str, nonce: str) -> str:
    settings = get_settings()
    payload = {"state": state, "nonce": nonce}
    return jose_jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def verify_state_cookie(token: str) -> dict:
    settings = get_settings()
    return jose_jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
