from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.instructor import Instructor
from app.models.user import User

router = APIRouter(prefix="/support-staff", tags=["support-staff"])


class SupportStaffOut(BaseModel):
    id: int
    name: str
    title: str | None

    class Config:
        from_attributes = True


@router.get("", response_model=list[SupportStaffOut])
async def list_support_staff(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(Instructor)
        .join(User, User.id == Instructor.user_id)
        .where(Instructor.school_wide == True)
        .order_by(User.last_name, User.first_name)
    )
    instructors = result.scalars().all()

    out = []
    for instructor in instructors:
        await db.refresh(instructor, ["user"])
        out.append(
            SupportStaffOut(
                id=instructor.id,
                name=f"{instructor.user.first_name} {instructor.user.last_name}".strip(),
                title=instructor.title,
            )
        )
    return out
