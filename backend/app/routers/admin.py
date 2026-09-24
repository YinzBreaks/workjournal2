from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Program, ProgramStudent, Staff, StaffKind, User, UserRole
from app.schemas import OverviewOut, ProgramSummaryOut
from app.security import require_role

router = APIRouter(prefix="/admin", tags=["admin"])

admin_only = require_role(UserRole.admin)


@router.get("/overview", response_model=OverviewOut)
async def overview(user: User = Depends(admin_only), db: AsyncSession = Depends(get_db)):
    async def count(stmt) -> int:
        return (await db.execute(stmt)).scalar_one()

    return OverviewOut(
        programs=await count(select(func.count(Program.id))),
        instructors=await count(
            select(func.count(Staff.id)).where(Staff.kind == StaffKind.instructor)
        ),
        assistants=await count(
            select(func.count(Staff.id)).where(Staff.kind == StaffKind.assistant)
        ),
        students=await count(
            select(func.count(User.id)).where(User.role == UserRole.student)
        ),
    )


@router.get("/programs", response_model=list[ProgramSummaryOut])
async def programs_summary(user: User = Depends(admin_only), db: AsyncSession = Depends(get_db)):
    programs = (await db.scalars(select(Program).order_by(Program.name))).unique().all()
    student_counts = dict(
        (
            await db.execute(
                select(ProgramStudent.program_id, func.count()).group_by(
                    ProgramStudent.program_id
                )
            )
        ).all()
    )
    return [
        ProgramSummaryOut(
            id=p.id,
            code=p.code,
            name=p.name,
            instructors=[s.user.display_name for s in p.staff if s.kind == StaffKind.instructor],
            assistants=[s.user.display_name for s in p.staff if s.kind == StaffKind.assistant],
            student_count=student_counts.get(p.id, 0),
        )
        for p in programs
    ]
