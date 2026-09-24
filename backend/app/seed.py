"""Load seed_data.py into the database. Safe to run repeatedly.

Usage (from backend/):
    python -m app.seed
"""

import asyncio

from sqlalchemy import select

from app import seed_data as data
from app.config import get_settings
from app.db import SessionLocal
from app.models import (
    Program,
    ProgramStudent,
    Project,
    Staff,
    StaffKind,
    Task,
    User,
    UserRole,
)
from app.provisioning import ensure_student_assignments


def _integration_username(display_name: str) -> str:
    return "integration." + display_name.lower().replace(" ", ".")


async def seed() -> None:
    code = get_settings().CLASS_PROGRAM_CODE
    async with SessionLocal() as db:
        program = await db.scalar(select(Program).where(Program.code == code))
        if program is None:
            name = data.PROGRAM["name"] if data.PROGRAM["code"] == code else code
            program = Program(code=code, name=name)
            db.add(program)
            await db.flush()

        integration: dict[str, Staff] = {}
        for display_name, title, phone in data.INTEGRATION:
            username = _integration_username(display_name)
            user = await db.scalar(select(User).where(User.username == username))
            if user is None:
                user = User(
                    username=username,
                    display_name=display_name,
                    email=f"{username}@beattietech.local",
                    role=UserRole.teacher,
                )
                db.add(user)
                await db.flush()
            staff = await db.scalar(select(Staff).where(Staff.user_id == user.id))
            if staff is None:
                staff = Staff(
                    user_id=user.id, kind=StaffKind.integration, title=title, phone=phone
                )
                db.add(staff)
                await db.flush()
            integration[display_name] = staff

        for spec in data.PROJECTS:
            project = await db.scalar(
                select(Project).where(
                    Project.program_id == program.id, Project.title == spec["title"]
                )
            )
            if project is None:
                project = Project(
                    program_id=program.id,
                    title=spec["title"],
                    description=spec["description"],
                )
                db.add(project)
                await db.flush()
            for position, (title, description, helper) in enumerate(spec["tasks"]):
                task = await db.scalar(
                    select(Task).where(Task.project_id == project.id, Task.title == title)
                )
                if task is None:
                    task = Task(
                        project_id=project.id,
                        title=title,
                        description=description,
                        position=position,
                    )
                    if helper:
                        task.support_staff = [integration[helper]]
                    db.add(task)
                    await db.flush()

        # Students who signed in before a task existed get it now.
        students = (
            await db.scalars(
                select(User)
                .join(ProgramStudent, ProgramStudent.student_id == User.id)
                .where(ProgramStudent.program_id == program.id)
            )
        ).all()
        for student in students:
            await ensure_student_assignments(db, student, program)

        await db.commit()
    print(f"Seeded {code}.")


if __name__ == "__main__":
    asyncio.run(seed())
