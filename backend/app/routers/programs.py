from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_role
from app.models.program import Program, ProgramStudent
from app.models.project import Project
from app.models.task import Assignment, AssignmentStatus
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


class SupportStaffOut(BaseModel):
    id: int
    name: str
    title: str | None

    class Config:
        from_attributes = True


class TaskStatsOut(BaseModel):
    not_started: int
    in_progress: int
    complete: int


class ProgramTaskOut(BaseModel):
    id: int
    title: str
    description: str
    order: int
    support_staff: list[SupportStaffOut]
    stats: TaskStatsOut


class ProgramProjectOut(BaseModel):
    id: int
    title: str
    description: str
    tasks: list[ProgramTaskOut]


@router.get("/{program_id}/projects", response_model=list[ProgramProjectOut])
async def list_program_projects(
    program_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(require_role("teacher", "admin"))],
):
    program = await db.get(Program, program_id)
    if program is None:
        raise HTTPException(status_code=404, detail="Program not found")

    result = await db.execute(select(Project).where(Project.program_id == program_id))
    projects = result.scalars().all()

    out = []
    for project in projects:
        await db.refresh(project, ["tasks"])
        tasks_out = []
        for task in sorted(project.tasks, key=lambda t: t.order):
            await db.refresh(task, ["support_staff"])
            staff_out = []
            for instructor in task.support_staff:
                await db.refresh(instructor, ["user"])
                staff_out.append(
                    SupportStaffOut(
                        id=instructor.id,
                        name=f"{instructor.user.first_name} {instructor.user.last_name}".strip(),
                        title=instructor.title,
                    )
                )

            result = await db.execute(
                select(Assignment.status, func.count())
                .where(Assignment.task_id == task.id)
                .group_by(Assignment.status)
            )
            counts = {status.value: 0 for status in AssignmentStatus}
            for status_value, count in result.all():
                counts[status_value.value] = count

            tasks_out.append(
                ProgramTaskOut(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    order=task.order,
                    support_staff=staff_out,
                    stats=TaskStatsOut(
                        not_started=counts["not_started"],
                        in_progress=counts["in_progress"],
                        complete=counts["complete"],
                    ),
                )
            )

        out.append(
            ProgramProjectOut(
                id=project.id,
                title=project.title,
                description=project.description,
                tasks=tasks_out,
            )
        )

    return out
