"""Load seed_data.py into the database. Safe to run repeatedly.

Usage (from backend/):
    python -m app.seed
"""

import asyncio
from datetime import date, timedelta

from sqlalchemy import select

from app import seed_data as data
from app.config import get_settings
from app.db import SessionLocal
from app.models import (
    Assignment,
    AssignmentStatus,
    Program,
    ProgramStaff,
    ProgramStudent,
    Project,
    Staff,
    StaffKind,
    Task,
    TaskSupportStaff,
    User,
    UserRole,
    WorkLog,
)
from app.security import hash_password


async def get_or_create(db, model, lookup: dict, defaults: dict | None = None):
    obj = await db.scalar(select(model).filter_by(**lookup))
    if obj is not None:
        return obj
    obj = model(**lookup, **(defaults or {}))
    db.add(obj)
    await db.flush()
    return obj


def username_for(first: str, last: str) -> str:
    return f"{first}.{last}".lower()


async def seed() -> None:
    settings = get_settings()
    missing = [
        name
        for name in ("ADMIN_PASS", "DEFAULT_STAFF_PASSWORD", "DEFAULT_STUDENT_PIN")
        if not getattr(settings, name)
    ]
    if missing:
        raise SystemExit(f"Set these in backend/.env before seeding: {', '.join(missing)}")

    # bcrypt is slow on purpose; hash each shared default once, not per user.
    staff_hash = hash_password(settings.DEFAULT_STAFF_PASSWORD)
    pin_hash = hash_password(settings.DEFAULT_STUDENT_PIN)

    async with SessionLocal() as db:
        await get_or_create(
            db,
            User,
            {"username": settings.ADMIN_USER},
            {
                "password_hash": hash_password(settings.ADMIN_PASS),
                "first_name": "Admin",
                "role": UserRole.admin,
            },
        )

        async def staff_member(first, last, kind, title, phone) -> Staff:
            user = await get_or_create(
                db,
                User,
                {"username": username_for(first, last)},
                {
                    "password_hash": staff_hash,
                    "first_name": first,
                    "last_name": last,
                    "role": UserRole.teacher,
                },
            )
            return await get_or_create(
                db, Staff, {"user_id": user.id}, {"kind": kind, "title": title, "phone": phone}
            )

        programs: dict[str, Program] = {}
        for entry in data.PROGRAMS:
            program = await get_or_create(
                db, Program, {"code": entry["code"]}, {"name": entry["name"]}
            )
            programs[entry["code"]] = program
            people = [(p, StaffKind.instructor, "Instructor") for p in entry["instructors"]] + [
                (p, StaffKind.assistant, "Instructional Assistant") for p in entry["assistants"]
            ]
            for (first, last, phone), kind, title in people:
                staff = await staff_member(first, last, kind, title, phone)
                await get_or_create(
                    db, ProgramStaff, {"program_id": program.id, "staff_id": staff.id}
                )

        for first, last, title, phone in data.LEARNING_SUPPORT:
            await staff_member(first, last, StaffKind.learning_support, title, phone)

        integration: dict[tuple[str, str], Staff] = {}
        for first, last, title, phone in data.INTEGRATION:
            integration[(first, last)] = await staff_member(
                first, last, StaffKind.integration, title, phone
            )

        students: dict[str, User] = {}
        for code, roster in data.STUDENTS.items():
            for username, first, last in roster:
                student = await get_or_create(
                    db,
                    User,
                    {"username": username},
                    {
                        "password_hash": pin_hash,
                        "first_name": first,
                        "last_name": last,
                        "role": UserRole.student,
                    },
                )
                students[username] = student
                await get_or_create(
                    db,
                    ProgramStudent,
                    {"program_id": programs[code].id, "student_id": student.id},
                )

        due = date.today() + timedelta(days=7)
        for code, spec in data.PROJECTS.items():
            project = await get_or_create(
                db,
                Project,
                {"program_id": programs[code].id, "title": spec["title"]},
                {"description": spec["description"]},
            )
            tasks = []
            for position, (title, description, helper) in enumerate(spec["tasks"]):
                task = await get_or_create(
                    db,
                    Task,
                    {"project_id": project.id, "title": title},
                    {"description": description, "position": position},
                )
                tasks.append(task)
                if helper is not None:
                    await get_or_create(
                        db,
                        TaskSupportStaff,
                        {"task_id": task.id, "staff_id": integration[helper].id},
                    )
            for username, statuses in spec["status"].items():
                for task, status_name in zip(tasks, statuses, strict=True):
                    status = AssignmentStatus(status_name)
                    await get_or_create(
                        db,
                        Assignment,
                        {"task_id": task.id, "student_id": students[username].id},
                        {
                            "status": status,
                            "due_date": None if status == AssignmentStatus.complete else due,
                        },
                    )

        # Dates are relative to today, so only add these to an empty table;
        # otherwise a rerun on a later day would duplicate them.
        if await db.scalar(select(WorkLog.id).limit(1)) is None:
            for username, code, days_ago, minutes, summary in data.WORK_LOGS:
                db.add(
                    WorkLog(
                        student_id=students[username].id,
                        program_id=programs[code].id,
                        date=date.today() - timedelta(days=days_ago),
                        minutes=minutes,
                        summary=summary,
                    )
                )

        await db.commit()

    print(
        f"Seeded {len(data.PROGRAMS)} programs and {len(students)} placeholder students. "
        f"Staff sign in as first.last with DEFAULT_STAFF_PASSWORD; "
        f"students use DEFAULT_STUDENT_PIN."
    )


if __name__ == "__main__":
    asyncio.run(seed())
