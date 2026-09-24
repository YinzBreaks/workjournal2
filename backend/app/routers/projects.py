"""Teachers building their class: create and remove projects and tasks.

A new task is assigned to every student enrolled in the program right away.
Students who join later get it on first sign-in (provisioning.py).
"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.errors import not_found
from app.models import Assignment, Program, ProgramStudent, Project, Task, User, UserRole
from app.ratelimit import limit_writes
from app.schemas import ProgramProjectOut, ProgramTaskOut, ProjectIn, TaskIn, TaskStatsOut
from app.security import ensure_program_access, require_role

router = APIRouter(tags=["projects"])

staff_only = require_role(UserRole.teacher, UserRole.admin)


async def _project_for(db: AsyncSession, user: User, project_id: int) -> Project:
    project = await db.get(Project, project_id)
    if project is None:
        raise not_found()
    await ensure_program_access(db, user, project.program_id)
    return project


@router.post(
    "/programs/{program_id}/projects",
    response_model=ProgramProjectOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    program_id: int,
    body: ProjectIn,
    user: User = Depends(staff_only),
    _: User = Depends(limit_writes),
    db: AsyncSession = Depends(get_db),
):
    await ensure_program_access(db, user, program_id)
    if await db.get(Program, program_id) is None:
        raise not_found()
    project = Project(
        program_id=program_id,
        title=body.title.strip(),
        description=body.description.strip(),
    )
    db.add(project)
    await db.commit()
    return ProgramProjectOut(
        id=project.id, title=project.title, description=project.description, tasks=[]
    )


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    user: User = Depends(staff_only),
    _: User = Depends(limit_writes),
    db: AsyncSession = Depends(get_db),
):
    """Removes the project, its tasks, and every student's progress on them."""
    project = await _project_for(db, user, project_id)
    await db.delete(project)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/projects/{project_id}/tasks",
    response_model=ProgramTaskOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    project_id: int,
    body: TaskIn,
    user: User = Depends(staff_only),
    _: User = Depends(limit_writes),
    db: AsyncSession = Depends(get_db),
):
    project = await _project_for(db, user, project_id)
    last = await db.scalar(
        select(func.max(Task.position)).where(Task.project_id == project.id)
    )
    task = Task(
        project_id=project.id,
        title=body.title.strip(),
        description=body.description.strip(),
        position=0 if last is None else last + 1,
    )
    db.add(task)
    await db.flush()

    student_ids = (
        await db.scalars(
            select(ProgramStudent.student_id).where(
                ProgramStudent.program_id == project.program_id
            )
        )
    ).all()
    for student_id in student_ids:
        db.add(Assignment(task_id=task.id, student_id=student_id))
    await db.commit()

    return ProgramTaskOut(
        id=task.id,
        title=task.title,
        description=task.description,
        support_staff=[],
        stats=TaskStatsOut(not_started=len(student_ids)),
    )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user: User = Depends(staff_only),
    _: User = Depends(limit_writes),
    db: AsyncSession = Depends(get_db),
):
    """Removes the task and every student's progress on it."""
    task = await db.get(Task, task_id)
    if task is None:
        raise not_found()
    await ensure_program_access(db, user, task.project.program_id)
    await db.delete(task)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
