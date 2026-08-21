from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_role
from app.models.instructor import Instructor
from app.models.program import Program, ProgramStudent
from app.models.user import User, UserRole

router = APIRouter(prefix="/admin", tags=["admin"])


class OverviewOut(BaseModel):
    programs: int
    instructors: int
    instructional_assistants: int
    students: int


class ProgramSummaryOut(BaseModel):
    id: int
    code: str
    name: str
    instructors: list[str]
    assistants: list[str]
    student_count: int


@router.get("/overview", response_model=OverviewOut)
async def overview(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(require_role("admin"))],
):
    program_count = (await db.execute(select(func.count(Program.id)))).scalar_one()

    instructor_count = (
        await db.execute(
            select(func.count(Instructor.id)).where(Instructor.title == "Instructor")
        )
    ).scalar_one()

    assistant_count = (
        await db.execute(
            select(func.count(Instructor.id)).where(
                Instructor.title == "Instructional Assistant"
            )
        )
    ).scalar_one()

    student_count = (
        await db.execute(
            select(func.count(User.id)).where(User.role == UserRole.student)
        )
    ).scalar_one()

    return OverviewOut(
        programs=program_count,
        instructors=instructor_count,
        instructional_assistants=assistant_count,
        students=student_count,
    )


@router.get("/programs", response_model=list[ProgramSummaryOut])
async def list_programs_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(require_role("admin"))],
):
    result = await db.execute(select(Program).order_by(Program.name))
    programs = result.scalars().all()

    out = []
    for program in programs:
        await db.refresh(program, ["instructors"])
        instructors = []
        assistants = []
        for instructor in program.instructors:
            await db.refresh(instructor, ["user"])
            name = f"{instructor.user.first_name} {instructor.user.last_name}".strip()
            if instructor.title == "Instructional Assistant":
                assistants.append(name)
            else:
                instructors.append(name)

        student_count = (
            await db.execute(
                select(func.count(ProgramStudent.id)).where(
                    ProgramStudent.program_id == program.id
                )
            )
        ).scalar_one()

        out.append(
            ProgramSummaryOut(
                id=program.id,
                code=program.code,
                name=program.name,
                instructors=instructors,
                assistants=assistants,
                student_count=student_count,
            )
        )

    return out
