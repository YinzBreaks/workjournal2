from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.errors import not_found
from app.models import (
    Assignment,
    Program,
    ProgramStaff,
    ProgramStudent,
    Project,
    Staff,
    Task,
    User,
    UserRole,
    WorkLog,
)
from app.schemas import (
    ProgramOut,
    ProgramProjectOut,
    ProgramTaskOut,
    RosterRowOut,
    TaskStatsOut,
    WorkLogOut,
    staff_out,
)
from app.routers.worklogs import worklog_out
from app.security import ensure_program_access, get_current_user

router = APIRouter(prefix="/programs", tags=["programs"])


@router.get("/mine", response_model=list[ProgramOut])
async def my_programs(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Students: programs they're enrolled in. Teachers: programs they staff."""
    stmt = select(Program).order_by(Program.name)
    if user.role == UserRole.student:
        stmt = stmt.join(ProgramStudent).where(ProgramStudent.student_id == user.id)
    elif user.role == UserRole.teacher:
        stmt = (
            stmt.join(ProgramStaff)
            .join(Staff, Staff.id == ProgramStaff.staff_id)
            .where(Staff.user_id == user.id)
        )
    result = await db.scalars(stmt)
    return result.unique().all()


@router.get("/{program_id}/roster", response_model=list[RosterRowOut])
async def program_roster(
    program_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Teacher view: each enrolled student with their total logged minutes."""
    await ensure_program_access(db, user, program_id)
    total = func.coalesce(func.sum(WorkLog.minutes), 0)
    rows = await db.execute(
        select(User.id, User.display_name, total)
        .join(ProgramStudent, ProgramStudent.student_id == User.id)
        .outerjoin(
            WorkLog,
            and_(WorkLog.student_id == User.id, WorkLog.program_id == program_id),
        )
        .where(ProgramStudent.program_id == program_id)
        .group_by(User.id)
        .order_by(User.display_name)
    )
    return [
        RosterRowOut(id=id_, name=name, total_minutes=minutes)
        for id_, name, minutes in rows.all()
    ]


@router.get("/{program_id}/students/{student_id}/worklogs", response_model=list[WorkLogOut])
async def student_worklogs(
    program_id: int,
    student_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Teacher view: one student's hour entries in this program, newest first.

    Only students enrolled in the program are visible; anyone else is a 404,
    so a teacher can't read other classes' students by guessing ids.
    """
    await ensure_program_access(db, user, program_id)
    if await db.get(ProgramStudent, (program_id, student_id)) is None:
        raise not_found()
    result = await db.scalars(
        select(WorkLog)
        .where(WorkLog.student_id == student_id, WorkLog.program_id == program_id)
        .order_by(WorkLog.date.desc(), WorkLog.id.desc())
    )
    return [worklog_out(log) for log in result.all()]


@router.get("/{program_id}/projects", response_model=list[ProgramProjectOut])
async def program_projects(
    program_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Teacher view: every project and task, with how many students are at each status."""
    await ensure_program_access(db, user, program_id)

    projects = (
        await db.scalars(
            select(Project).where(Project.program_id == program_id).order_by(Project.position, Project.id)
        )
    ).all()
    tasks = (
        await db.scalars(
            select(Task)
            .where(Task.project_id.in_([p.id for p in projects]))
            .order_by(Task.position, Task.id)
        )
    ).all()

    counts = await db.execute(
        select(Assignment.task_id, Assignment.status, func.count())
        .where(Assignment.task_id.in_([t.id for t in tasks]))
        .group_by(Assignment.task_id, Assignment.status)
    )
    stats: dict[int, TaskStatsOut] = {t.id: TaskStatsOut() for t in tasks}
    for task_id, status_, count in counts.all():
        setattr(stats[task_id], status_.value, count)

    return [
        ProgramProjectOut(
            id=p.id,
            title=p.title,
            description=p.description,
            tasks=[
                ProgramTaskOut(
                    id=t.id,
                    title=t.title,
                    description=t.description,
                    support_staff=[staff_out(s) for s in t.support_staff],
                    stats=stats[t.id],
                )
                for t in tasks
                if t.project_id == p.id
            ],
        )
        for p in projects
    ]
