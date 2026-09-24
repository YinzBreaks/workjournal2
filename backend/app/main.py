from fastapi import APIRouter, FastAPI

from app.routers import admin, assignments, auth, programs, tasks, worklogs

app = FastAPI(title="Beattie Journal")

api = APIRouter(prefix="/api")


@api.get("/health")
async def health():
    return {"status": "ok"}


for module in (auth, programs, assignments, worklogs, tasks, admin):
    api.include_router(module.router)

app.include_router(api)
