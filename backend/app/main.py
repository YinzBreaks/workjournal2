"""The API under /api, plus the built frontend (in Docker) at everything else."""

from pathlib import Path

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.routers import admin, assignments, auth, programs, projects, tasks, worklogs

MAX_BODY_BYTES = 16 * 1024

# Set by the Dockerfile; absent in local dev, where Vite serves the frontend.
FRONTEND_DIST = Path(__file__).resolve().parents[1] / "static"

app = FastAPI(title="Beattie Journal", docs_url=None, redoc_url=None, openapi_url=None)


@app.middleware("http")
async def reject_large_bodies(request: Request, call_next):
    length = request.headers.get("content-length")
    if length is not None and (not length.isdigit() or int(length) > MAX_BODY_BYTES):
        return JSONResponse(status_code=413, content={"detail": "too_large"})
    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc: RequestValidationError):
    # A code, not pydantic's English, so the frontend can translate it.
    return JSONResponse(status_code=422, content={"detail": "invalid_request"})


api = APIRouter(prefix="/api")


@api.get("/health")
async def health():
    return {"status": "ok"}


for module in (auth, programs, projects, assignments, worklogs, tasks, admin):
    api.include_router(module.router)

app.include_router(api)


if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    async def spa(path: str):
        if path.startswith("api/"):
            return JSONResponse(status_code=404, content={"detail": "not_found"})
        file = (FRONTEND_DIST / path).resolve()
        if path and file.is_file() and FRONTEND_DIST in file.parents:
            return FileResponse(file)
        return FileResponse(FRONTEND_DIST / "index.html")
