"""Turn an Authelia identity into a User, and set up their class on first visit.

Students are enrolled in the class program and given every task in it.
Teachers are linked to the class program as instructors. Admins need nothing.
"""

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import (
    Assignment,
    Program,
    ProgramStaff,
    ProgramStudent,
    Project,
    Staff,
    StaffKind,
    Task,
    User,
    UserRole,
)

if TYPE_CHECKING:
    from app.security import Identity


async def class_program(db: AsyncSession) -> Program | None:
    code = get_settings().CLASS_PROGRAM_CODE
    return await db.scalar(select(Program).where(Program.code == code))


async def ensure_student_assignments(db: AsyncSession, student: User, program: Program) -> None:
    """Give a student an Assignment for every task in the program they lack."""
    task_ids = (
        await db.scalars(
            select(Task.id).join(Project).where(Project.program_id == program.id)
        )
    ).all()
    have = set(
        (
            await db.scalars(
                select(Assignment.task_id).where(Assignment.student_id == student.id)
            )
        ).all()
    )
    for task_id in task_ids:
        if task_id not in have:
            db.add(Assignment(task_id=task_id, student_id=student.id))


async def _set_up_class(db: AsyncSession, user: User) -> None:
    program = await class_program(db)
    if program is None:
        return
    if user.role == UserRole.student:
        if await db.get(ProgramStudent, (program.id, user.id)) is None:
            db.add(ProgramStudent(program_id=program.id, student_id=user.id))
        await ensure_student_assignments(db, user, program)
    elif user.role == UserRole.teacher:
        staff = await db.scalar(select(Staff).where(Staff.user_id == user.id))
        if staff is None:
            staff = Staff(user_id=user.id, kind=StaffKind.instructor, title="Instructor")
            db.add(staff)
            await db.flush()
        if staff.kind in (StaffKind.instructor, StaffKind.assistant):
            if await db.get(ProgramStaff, (program.id, staff.id)) is None:
                db.add(ProgramStaff(program_id=program.id, staff_id=staff.id))


async def sync_user(db: AsyncSession, identity: "Identity") -> User:
    """Find or create the user for this identity, keeping name/email/role current."""
    user = await db.scalar(select(User).where(User.username == identity.username))

    if user is None:
        user = User(
            username=identity.username,
            display_name=identity.name,
            email=identity.email,
            role=identity.role,
        )
        db.add(user)
        try:
            await db.flush()
        except IntegrityError:
            # A parallel first request created them a moment ago.
            await db.rollback()
            return await db.scalar(select(User).where(User.username == identity.username))
        await _set_up_class(db, user)
        await db.commit()
        return user

    changed_role = user.role != identity.role
    if changed_role or (user.display_name, user.email) != (identity.name, identity.email):
        user.display_name = identity.name
        user.email = identity.email
        user.role = identity.role
        if changed_role:
            await _set_up_class(db, user)
        await db.commit()
    return user
