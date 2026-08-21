from typing import Annotated

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_role
from app.models.program import Program
from app.models.project import Project
from app.models.student_project import StudentProject
from app.models.task import Assignment, Task

router = APIRouter(prefix="/students", tags=["students"])


class ProgramRef(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True


class SupportStaffOut(BaseModel):
    id: int
    name: str
    title: str | None

    class Config:
        from_attributes = True


class AssignmentOut(BaseModel):
    id: int
    status: str
    due_date: str | None


class StudentTaskOut(BaseModel):
    id: int
    title: str
    description: str
    order: int
    support_staff: list[SupportStaffOut]
    assignment: AssignmentOut | None


class StudentProjectOut(BaseModel):
    id: int
    title: str
    description: str
    program: ProgramRef
    tasks: list[StudentTaskOut]


@router.get("/me/projects", response_model=list[StudentProjectOut])
async def my_projects(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(require_role("student"))],
):
    student_id = current_user["user_id"]

    result = await db.execute(
        select(StudentProject).where(StudentProject.student_id == student_id)
    )
    student_projects = result.scalars().all()

    out = []
    for sp in student_projects:
        await db.refresh(sp, ["project"])
        project = sp.project
        await db.refresh(project, ["tasks", "program"])

        task_ids = [t.id for t in project.tasks]
        assignments_by_task = {}
        if task_ids:
            result = await db.execute(
                select(Assignment).where(
                    Assignment.task_id.in_(task_ids),
                    Assignment.student_project_id == sp.id,
                )
            )
            for a in result.scalars().all():
                assignments_by_task[a.task_id] = a

        tasks_out = []
        for t in sorted(project.tasks, key=lambda x: x.order):
            await db.refresh(t, ["support_staff"])
            staff_out = []
            for instructor in t.support_staff:
                await db.refresh(instructor, ["user"])
                staff_out.append(
                    SupportStaffOut(
                        id=instructor.id,
                        name=f"{instructor.user.first_name} {instructor.user.last_name}".strip(),
                        title=instructor.title,
                    )
                )

            assignment = assignments_by_task.get(t.id)
            tasks_out.append(
                StudentTaskOut(
                    id=t.id,
                    title=t.title,
                    description=t.description,
                    order=t.order,
                    support_staff=staff_out,
                    assignment=(
                        AssignmentOut(
                            id=assignment.id,
                            status=assignment.status.value,
                            due_date=(
                                assignment.due_date.isoformat()
                                if assignment.due_date
                                else None
                            ),
                        )
                        if assignment
                        else None
                    ),
                )
            )

        out.append(
            StudentProjectOut(
                id=project.id,
                title=project.title,
                description=project.description,
                program=ProgramRef(
                    id=project.program.id,
                    code=project.program.code,
                    name=project.program.name,
                ),
                tasks=tasks_out,
            )
        )

    return out
