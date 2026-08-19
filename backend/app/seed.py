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

SEED_PROGRAMS = [
    {
        "code": "WOODSHOP-101",
        "name": "Intro to Woodshop",
        "teacher": {
            "username": "teacher.rivera",
            "email": "d.rivera@example.edu",
            "first_name": "Dana",
            "last_name": "Rivera",
        },
        "students": [
            {"username": "student.alex", "first_name": "Alex", "last_name": "Chen"},
            {"username": "student.jordan", "first_name": "Jordan", "last_name": "Patel"},
            {"username": "student.sam", "first_name": "Sam", "last_name": "Okafor"},
        ],
    },
    {
        "code": "WELD-101",
        "name": "Welding Fundamentals",
        "teacher": {
            "username": "teacher.webb",
            "email": "m.webb@example.edu",
            "first_name": "Marcus",
            "last_name": "Webb",
        },
        "students": [
            {"username": "student.jordan", "first_name": "Jordan", "last_name": "Patel"},
            {"username": "student.taylor", "first_name": "Taylor", "last_name": "Brooks"},
        ],
    },
    {
        "code": "AUTO-101",
        "name": "Automotive Technology",
        "teacher": {
            "username": "teacher.nair",
            "email": "p.nair@example.edu",
            "first_name": "Priya",
            "last_name": "Nair",
        },
        "students": [
            {"username": "student.morgan", "first_name": "Morgan", "last_name": "Lee"},
            {"username": "student.casey", "first_name": "Casey", "last_name": "Reyes"},
        ],
    },
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


async def get_or_create_program(db, *, code, name) -> tuple[Program, bool]:
    result = await db.execute(select(Program).where(Program.code == code))
    program = result.scalar_one_or_none()
    if program is not None:
        return program, False

    program = Program(code=code, name=name)
    db.add(program)
    await db.flush()
    return program, True


async def get_or_create_instructor(db, *, user_id) -> Instructor:
    result = await db.execute(select(Instructor).where(Instructor.user_id == user_id))
    instructor = result.scalar_one_or_none()
    if instructor is not None:
        return instructor

    instructor = Instructor(user_id=user_id)
    db.add(instructor)
    await db.flush()
    return instructor


async def link_program_instructor(db, *, program_id, instructor_id) -> bool:
    result = await db.execute(
        select(ProgramInstructor).where(
            ProgramInstructor.program_id == program_id,
            ProgramInstructor.instructor_id == instructor_id,
        )
    )
    if result.scalar_one_or_none() is not None:
        return False

    db.add(ProgramInstructor(program_id=program_id, instructor_id=instructor_id))
    return True


async def enroll_student(db, *, program_id, student_id) -> bool:
    result = await db.execute(
        select(ProgramStudent).where(
            ProgramStudent.program_id == program_id,
            ProgramStudent.student_id == student_id,
        )
    )
    if result.scalar_one_or_none() is not None:
        return False

    db.add(ProgramStudent(program_id=program_id, student_id=student_id))
    return True


async def seed() -> None:
    settings = get_settings()
    session_factory = get_async_session_factory()
    default_pin = settings.DEFAULT_STUDENT_PIN or "0000"

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

        for entry in SEED_PROGRAMS:
            program, created = await get_or_create_program(
                db, code=entry["code"], name=entry["name"]
            )
            print(f"{'Created' if created else 'Found'} program: {program.code}")

            t = entry["teacher"]
            teacher, created = await get_or_create_user(
                db,
                username=t["username"],
                defaults=dict(
                    email=t["email"],
                    password_hash=hash_password("dev-password"),
                    first_name=t["first_name"],
                    last_name=t["last_name"],
                    role=UserRole.teacher,
                ),
            )
            print(f"  {'Created' if created else 'Found'} teacher: {teacher.username}")

            instructor = await get_or_create_instructor(db, user_id=teacher.id)
            if await link_program_instructor(
                db, program_id=program.id, instructor_id=instructor.id
            ):
                print(f"  Linked {teacher.username} to {program.code}")

            for s in entry["students"]:
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
                print(f"  {'Created' if created else 'Found'} student: {student.username}")

                if await enroll_student(
                    db, program_id=program.id, student_id=student.id
                ):
                    print(f"  Enrolled {student.username} in {program.code}")

        await db.commit()
        print(f"\nSeed complete. Student PIN for login: {default_pin}")


if __name__ == "__main__":
    asyncio.run(seed())
