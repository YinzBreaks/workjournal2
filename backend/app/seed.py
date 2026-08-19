"""Seed baseline data for local development.

Usage:
    PYTHONPATH=. python -m app.seed
"""
import asyncio

from sqlalchemy import select

from app.config import get_settings
from app.models import (
    Instructor,
    Program,
    ProgramInstructor,
    ProgramStudent,
    User,
    UserRole,
    get_async_session_factory,
)
from app.services.auth import hash_password

SEED_PROGRAM_CODE = "WOODSHOP-101"
SEED_PROGRAM_NAME = "Intro to Woodshop"

SEED_TEACHER = {
    "username": "teacher.demo",
    "email": "teacher.demo@example.com",
    "first_name": "Dana",
    "last_name": "Rivera",
}

SEED_STUDENTS = [
    {"username": "student.alex", "first_name": "Alex", "last_name": "Chen"},
    {"username": "student.jordan", "first_name": "Jordan", "last_name": "Patel"},
    {"username": "student.sam", "first_name": "Sam", "last_name": "Okafor"},
]


async def get_or_create_user(db, *, username, defaults) -> tuple[User, bool]:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is not None:
        return user, False

    user = User(username=username, **defaults)
    db.add(user)
    await db.flush()
    return user, True


async def seed() -> None:
    settings = get_settings()
    session_factory = get_async_session_factory()

    async with session_factory() as db:
        # --- Admin ---
        admin, created = await get_or_create_user(
            db,
            username=settings.ADMIN_USER,
            defaults=dict(
                email=settings.ADMIN_USER if "@" in settings.ADMIN_USER else None,
                password_hash=hash_password(settings.ADMIN_PASS or "change-me"),
                first_name="Admin",
                last_name="",
                role=UserRole.admin,
            ),
        )
        print(f"{'Created' if created else 'Found'} admin: {admin.username}")

        # --- Program ---
        result = await db.execute(
            select(Program).where(Program.code == SEED_PROGRAM_CODE)
        )
        program = result.scalar_one_or_none()
        if program is None:
            program = Program(code=SEED_PROGRAM_CODE, name=SEED_PROGRAM_NAME)
            db.add(program)
            await db.flush()
            print(f"Created program: {program.code}")
        else:
            print(f"Found program: {program.code}")

        # --- Teacher + Instructor ---
        teacher, created = await get_or_create_user(
            db,
            username=SEED_TEACHER["username"],
            defaults=dict(
                email=SEED_TEACHER["email"],
                password_hash=hash_password("dev-password"),
                first_name=SEED_TEACHER["first_name"],
                last_name=SEED_TEACHER["last_name"],
                role=UserRole.teacher,
            ),
        )
        print(f"{'Created' if created else 'Found'} teacher: {teacher.username}")

        result = await db.execute(
            select(Instructor).where(Instructor.user_id == teacher.id)
        )
        instructor = result.scalar_one_or_none()
        if instructor is None:
            instructor = Instructor(user_id=teacher.id)
            db.add(instructor)
            await db.flush()

        result = await db.execute(
            select(ProgramInstructor).where(
                ProgramInstructor.program_id == program.id,
                ProgramInstructor.instructor_id == instructor.id,
            )
        )
        if result.scalar_one_or_none() is None:
            db.add(
                ProgramInstructor(
                    program_id=program.id, instructor_id=instructor.id
                )
            )
            print(f"Linked instructor {teacher.username} to {program.code}")

        # --- Students ---
        default_pin = settings.DEFAULT_STUDENT_PIN or "0000"
        for s in SEED_STUDENTS:
            student, created = await get_or_create_user(
                db,
                username=s["username"],
                defaults=dict(
                    email=None,
                    password_hash=hash_password(default_pin),
                    first_name=s["first_name"],
                    last_name=s["last_name"],
                    role=UserRole.student,
                ),
            )
            print(f"{'Created' if created else 'Found'} student: {student.username}")

            result = await db.execute(
                select(ProgramStudent).where(
                    ProgramStudent.program_id == program.id,
                    ProgramStudent.student_id == student.id,
                )
            )
            if result.scalar_one_or_none() is None:
                db.add(
                    ProgramStudent(program_id=program.id, student_id=student.id)
                )
                print(f"Enrolled {student.username} in {program.code}")

        await db.commit()
        print(f"\nSeed complete. Student PIN for login: {default_pin}")


if __name__ == "__main__":
    asyncio.run(seed())
