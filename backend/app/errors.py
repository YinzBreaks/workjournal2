"""Every error the API returns is a short code, never English text.

The frontend translates `errors.<code>` from its locale files, so each code
used here must exist in frontend/src/i18n/locales/*.json.
"""

from fastapi import HTTPException, status


def api_error(status_code: int, code: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail=code)


def not_signed_in() -> HTTPException:
    return api_error(status.HTTP_401_UNAUTHORIZED, "not_signed_in")


def account_disabled() -> HTTPException:
    return api_error(status.HTTP_403_FORBIDDEN, "account_disabled")


def forbidden() -> HTTPException:
    return api_error(status.HTTP_403_FORBIDDEN, "forbidden")


def not_found() -> HTTPException:
    return api_error(status.HTTP_404_NOT_FOUND, "not_found")


def bad_request(code: str) -> HTTPException:
    return api_error(status.HTTP_400_BAD_REQUEST, code)


def rate_limited() -> HTTPException:
    return api_error(status.HTTP_429_TOO_MANY_REQUESTS, "rate_limited")
