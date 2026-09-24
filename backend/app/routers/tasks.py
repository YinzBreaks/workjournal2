"""Tagging school-wide support staff ("ask Jen Groomes for math help") on a task."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.errors import bad_request, not_found
from app.models import Staff, StaffKind, Task, User, UserRole
from app.ratelimit import limit_writes
from app.schemas import StaffOut, TagStaffIn, staff_out
from app.security import ensure_program_access, get_current_user, require_role

router = APIRouter(tags=["tasks"])

staff_only = require_role(UserRole.teacher, UserRole.admin)


@router.get("/support-staff", response_model=list[StaffOut])
async def list_support_staff(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.scalars(select(Staff).where(Staff.kind == StaffKind.integration))
    staff = sorted(result.unique().all(), key=lambda s: s.user.display_name)
    return [staff_out(s) for s in staff]


async def _task_for(db: AsyncSession, user: User, task_id: int) -> Task:
    task = await db.get(Task, task_id)
    if task is None:
        raise not_found()
    await ensure_program_access(db, user, task.project.program_id)
    return task


@router.post("/tasks/{task_id}/support-staff", response_model=list[StaffOut])
async def tag_support_staff(
    task_id: int,
    body: TagStaffIn,
    user: User = Depends(staff_only),
    _: User = Depends(limit_writes),
    db: AsyncSession = Depends(get_db),
):
    task = await _task_for(db, user, task_id)
    staff = await db.get(Staff, body.staff_id)
    if staff is None or staff.kind != StaffKind.integration:
        raise bad_request("integration_only")
    if all(s.id != staff.id for s in task.support_staff):
        task.support_staff.append(staff)
        await db.commit()
    return [staff_out(s) for s in task.support_staff]


@router.delete("/tasks/{task_id}/support-staff/{staff_id}", response_model=list[StaffOut])
async def untag_support_staff(
    task_id: int,
    staff_id: int,
    user: User = Depends(staff_only),
    _: User = Depends(limit_writes),
    db: AsyncSession = Depends(get_db),
):
    task = await _task_for(db, user, task_id)
    task.support_staff = [s for s in task.support_staff if s.id != staff_id]
    await db.commit()
    return [staff_out(s) for s in task.support_staff]
