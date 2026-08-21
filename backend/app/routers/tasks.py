from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_role
from app.models.instructor import Instructor
from app.models.task import Task, TaskSupportStaff
from app.models.user import User

router = APIRouter(prefix="/tasks", tags=["tasks"])


class SupportStaffOut(BaseModel):
    id: int
    name: str
    title: str | None

    class Config:
        from_attributes = True


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    order: int
    support_staff: list[SupportStaffOut]

    class Config:
        from_attributes = True


class AddSupportStaffRequest(BaseModel):
    instructor_id: int


async def _serialize_task(db: AsyncSession, task: Task) -> TaskOut:
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
    return TaskOut(
        id=task.id,
        title=task.title,
        description=task.description,
        order=task.order,
        support_staff=staff_out,
    )


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return await _serialize_task(db, task)


@router.post("/{task_id}/support-staff", response_model=TaskOut)
async def add_task_support_staff(
    task_id: int,
    body: AddSupportStaffRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(require_role("teacher", "admin"))],
):
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    instructor = await db.get(Instructor, body.instructor_id)
    if instructor is None:
        raise HTTPException(status_code=404, detail="Instructor not found")
    if not instructor.school_wide:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only school-wide support staff can be tagged on a task",
        )

    result = await db.execute(
        select(TaskSupportStaff).where(
            TaskSupportStaff.task_id == task_id,
            TaskSupportStaff.instructor_id == body.instructor_id,
        )
    )
    if result.scalar_one_or_none() is None:
        db.add(TaskSupportStaff(task_id=task_id, instructor_id=body.instructor_id))
        await db.commit()

    return await _serialize_task(db, task)


@router.delete("/{task_id}/support-staff/{instructor_id}", response_model=TaskOut)
async def remove_task_support_staff(
    task_id: int,
    instructor_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(require_role("teacher", "admin"))],
):
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    result = await db.execute(
        select(TaskSupportStaff).where(
            TaskSupportStaff.task_id == task_id,
            TaskSupportStaff.instructor_id == instructor_id,
        )
    )
    link = result.scalar_one_or_none()
    if link is not None:
        await db.delete(link)
        await db.commit()

    return await _serialize_task(db, task)
