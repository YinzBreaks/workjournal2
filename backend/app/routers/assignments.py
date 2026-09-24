from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.errors import not_found
from app.models import Assignment, User, UserRole
from app.ratelimit import limit_writes
from app.schemas import AssignmentOut, AssignmentUpdateIn, staff_out
from app.security import ensure_program_access, require_role

router = APIRouter(prefix="/assignments", tags=["assignments"])


def assignment_out(a: Assignment) -> AssignmentOut:
    return AssignmentOut(
        id=a.id,
        status=a.status,
        due_date=a.due_date,
        task_id=a.task.id,
        task_title=a.task.title,
        task_description=a.task.description,
        project_title=a.task.project.title,
        program_name=a.task.project.program.name,
        support_staff=[staff_out(s) for s in a.task.support_staff],
    )


@router.get("", response_model=list[AssignmentOut])
async def my_assignments(
    user: User = Depends(require_role(UserRole.student)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.scalars(select(Assignment).where(Assignment.student_id == user.id))
    assignments = sorted(
        result.unique().all(), key=lambda a: (a.task.project_id, a.task.position, a.task.id)
    )
    return [assignment_out(a) for a in assignments]


@router.patch("/{assignment_id}", response_model=AssignmentOut)
async def update_assignment(
    assignment_id: int,
    body: AssignmentUpdateIn,
    user: User = Depends(limit_writes),
    db: AsyncSession = Depends(get_db),
):
    """Move a task between Not started / In progress / Complete."""
    assignment = await db.get(Assignment, assignment_id)
    if assignment is None:
        raise not_found()

    if user.role == UserRole.student:
        # 404, not 403: don't reveal that someone else's assignment exists.
        if assignment.student_id != user.id:
            raise not_found()
    else:
        await ensure_program_access(db, user, assignment.task.project.program_id)

    assignment.status = body.status
    await db.commit()
    return assignment_out(assignment)
