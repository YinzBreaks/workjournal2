from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.program import Program, ProgramStudent
from app.models.user import User, UserRole

router = APIRouter(prefix="/programs", tags=["programs"])


class ProgramOut(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True


class StudentOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


@router.get("", response_model=list[ProgramOut])
async def list_programs(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Program).order_by(Program.name))
    return result.scalars().all()


@router.get("/{program_id}/students", response_model=list[StudentOut])
async def list_program_students(
    program_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    program = await db.get(Program, program_id)
    if program is None:
        raise HTTPException(status_code=404, detail="Program not found")

    result = await db.execute(
        select(User)
        .join(ProgramStudent, ProgramStudent.student_id == User.id)
        .where(
            ProgramStudent.program_id == program_id,
            User.role == UserRole.student,
            User.active == True,
        )
        .order_by(User.last_name, User.first_name)
    )
    students = result.scalars().all()
    return [
        StudentOut(id=s.id, name=f"{s.first_name} {s.last_name}".strip())
        for s in students
    ]
