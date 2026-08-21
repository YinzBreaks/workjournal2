from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_role
from app.models.instructor import Instructor

router = APIRouter(prefix="/teachers", tags=["teachers"])


class ProgramOut(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True


@router.get("/me/programs", response_model=list[ProgramOut])
async def my_programs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(require_role("teacher"))],
):
    result = await db.execute(
        select(Instructor).where(Instructor.user_id == current_user["user_id"])
    )
    instructor = result.scalar_one_or_none()
    if instructor is None:
        raise HTTPException(status_code=404, detail="Instructor record not found")

    await db.refresh(instructor, ["programs"])
    return sorted(instructor.programs, key=lambda p: p.name)
