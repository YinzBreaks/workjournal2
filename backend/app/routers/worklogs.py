from datetime import date

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.errors import bad_request, not_found
from app.models import ProgramStudent, User, UserRole, WorkLog
from app.ratelimit import limit_writes
from app.schemas import WorkLogIn, WorkLogOut
from app.security import require_role

router = APIRouter(prefix="/worklogs", tags=["worklogs"])

student_only = require_role(UserRole.student)


def worklog_out(log: WorkLog) -> WorkLogOut:
    return WorkLogOut(
        id=log.id,
        program_id=log.program_id,
        program_name=log.program.name,
        date=log.date,
        minutes=log.minutes,
        summary=log.summary,
    )


@router.get("", response_model=list[WorkLogOut])
async def my_worklogs(user: User = Depends(student_only), db: AsyncSession = Depends(get_db)):
    result = await db.scalars(
        select(WorkLog)
        .where(WorkLog.student_id == user.id)
        .order_by(WorkLog.date.desc(), WorkLog.id.desc())
    )
    return [worklog_out(log) for log in result.all()]


@router.post("", response_model=WorkLogOut, status_code=status.HTTP_201_CREATED)
async def create_worklog(
    body: WorkLogIn,
    user: User = Depends(student_only),
    _: User = Depends(limit_writes),
    db: AsyncSession = Depends(get_db),
):
    enrolled = await db.get(ProgramStudent, (body.program_id, user.id))
    if enrolled is None:
        raise bad_request("not_enrolled")
    if body.date > date.today():
        raise bad_request("future_date")

    log = WorkLog(student_id=user.id, **body.model_dump())
    db.add(log)
    await db.commit()
    await db.refresh(log, ["program"])
    return worklog_out(log)


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_worklog(
    log_id: int,
    user: User = Depends(student_only),
    _: User = Depends(limit_writes),
    db: AsyncSession = Depends(get_db),
):
    log = await db.get(WorkLog, log_id)
    if log is None or log.student_id != user.id:
        raise not_found()
    await db.delete(log)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
