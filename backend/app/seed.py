"""Seed the school's real programs and staff directory for local development.

Source: the school's "Instructors and Learning Support" staff directory.
Student data is NOT real — no roster was provided, and real students'
names aren't something to invent, so a small set of placeholder students
is enrolled in a few real programs just to exercise the login flow.

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

TITLE_INSTRUCTOR = "Instructor"
TITLE_ASSISTANT = "Instructional Assistant"

# Each program: its code/name, lead instructors, and instructional
# assistants. A person appearing under multiple programs (e.g. Paula
# Gibson) is only created once and linked to each program.
PROGRAMS = [
    {
        "code": "ADV-DESIGN",
        "name": "Advertising Design",
        "instructors": [("Andrew", "Dumbeck", "412.847.1917"), ("Jessica", "Lingsch", "412.847.1951")],
        "assistants": [],
    },
    {
        "code": "AUTO-COLLISION",
        "name": "Automotive Collision Technology",
        "instructors": [("Pat", "Ciccone", "412.847.1941"), ("Joe", "Pelesky", "412.847.1942")],
        "assistants": [("Jim", "Meinert", "412.847.1841")],
    },
    {
        "code": "AUTO-TECH",
        "name": "Automotive Technology",
        "instructors": [
            ("Rick", "Bennett", "412.847.1948"),
            ("Jonathan", "Mansfield", "412.847.1922"),
            ("Nathan", "Monroe", "412.847.1949"),
        ],
        "assistants": [("Eric", "Szelc", "412.847.1948")],
    },
    {
        "code": "CARPENTRY",
        "name": "Carpentry/Building Construction",
        "instructors": [
            ("Cam", "Galloway", "412.847.1943"),
            ("John", "Brown", "412.847.1944"),
            ("Dale", "Dankmyer", "412.847.1956"),
        ],
        "assistants": [("Noah", "Pare", "412.847.1944")],
    },
    {
        "code": "COSMETOLOGY",
        "name": "Cosmetology",
        "instructors": [
            ("Sarah", "Nolan", "412.847.1927"),
            ("Cynthia", "Cazin", "412.847.1928"),
            ("Joani", "Zelazowski", "412.847.1929"),
            ("Stevie", "Slogan", "412.847.1923"),
        ],
        "assistants": [("Anna", "Yourish", "412.847.1928")],
    },
    {
        "code": "CULINARY",
        "name": "Culinary Arts",
        "instructors": [("Evelyn", "Sussman", "412.847.1916"), ("Aaron", "Yurek", "412.847.1933")],
        "assistants": [("Ashton", "Monroe", "412.847.1931")],
    },
    {
        "code": "DENTAL",
        "name": "Dental Careers",
        "instructors": [("Paula", "Gibson", "412.847.1936")],
        "assistants": [],
    },
    {
        "code": "ECE",
        "name": "Early Childhood Education",
        "instructors": [("Cari", "Ludwig", "412.847.1926")],
        "assistants": [("Diane", "Murray", "412.847.1926")],
    },
    {
        "code": "ERT",
        "name": "Emergency Response Technology",
        "instructors": [("Lee", "Silnutzer", "412.847.1938")],
        "assistants": [("Alexa", "Kurta", "412.847.1938")],
    },
    {
        "code": "HEALTH-NURSING",
        "name": "Health and Nursing Sciences",
        "instructors": [("Sarah", "Dietz", "412.847.1937"), ("Douglas", "Moran", "412.847.1939")],
        "assistants": [("Hilary", "Falo", "412.847.1937")],
    },
    {
        "code": "HVAC",
        "name": "HVAC",
        "instructors": [("Charles", "Wike", "412.847.1945"), ("Roy", "Hughes", "412.847.1946")],
        "assistants": [("Joe", "Goodyear", "412.847.1945")],
    },
    {
        "code": "NETWORK-CYBER",
        "name": "Network Engineering and Cyber Security",
        "instructors": [("Michael", "Lingsch", "412.847.1952")],
        "assistants": [("Michael", "Powers", "412.847.1952")],
    },
    {
        "code": "PHARMACY",
        "name": "Introduction to Pharmacy",
        "instructors": [("Paula", "Gibson", "412.847.1936")],
        "assistants": [],
    },
    {
        "code": "PASTRY",
        "name": "Pastry Arts",
        "instructors": [("Ken", "Morehead", "412.847.1932")],
        "assistants": [],
    },
    {
        "code": "ROBOTICS",
        "name": "Robotics Engineering Technology",
        "instructors": [("Michael", "Purucker", "412.847.1953")],
        "assistants": [],
    },
    {
        "code": "SPORTS-MED",
        "name": "Sports Medicine",
        "instructors": [("Darren", "Vtipil", "412.847.1964"), ("Chris", "Cowger", "412.847.1965")],
        "assistants": [],
    },
    {
        "code": "SURGICAL",
        "name": "Surgical Sciences",
        "instructors": [("Vincenzina", "Olszewski", "412.847.1954")],
        "assistants": [],
    },
    {
        "code": "VET-SCIENCE",
        "name": "Veterinary Sciences",
        "instructors": [("Megan", "Chuckery", "412.847.1883"), ("Jennifer", "Dumbeck", "412.847.1886")],
        "assistants": [],
    },
]

# Not tied to any one program.
LEARNING_SUPPORT = [
    ("John", "Ellis", "Learning Support", "412.847.1931"),
    ("Erin", "Brennan", "Learning Support", "412.847.1924"),
    ("Bella", "Ellis", "Learning Support", "412.847.1959"),
    ("Erin", "Rushe", "Special Populations Coord.", "412.847.1925"),
    ("Jonathan", "Chuckery", "Educational Support", "412.847.1947"),
]

# School-wide: work with all students, not assigned to a program. Marked
# school_wide=True so they show up in GET /api/support-staff for teachers
# to tag onto tasks.
INTEGRATION_INSTRUCTORS = [
    ("Gretchen", "Boyette", "English Language Learners Coord.", "412.847.1913"),
    ("Jen", "Groomes", "Math Integration", "412.847.1958"),
    ("Tad", "Thayer", "Science Integration", "412.847.1957"),
    ("Nicholas", "Sauer", "Student Engagement Specialist", "412.847.1934"),
]

# No real student roster was provided. These placeholders are enrolled in
# a few of the real programs above just so the login flow has something
# to click through.
PLACEHOLDER_STUDENTS = {
    "AUTO-TECH": [
        {"username": "student.alex", "first_name": "Alex", "last_name": "Chen"},
        {"username": "student.jordan", "first_name": "Jordan", "last_name": "Patel"},
    ],
    "CULINARY": [
        {"username": "student.sam", "first_name": "Sam", "last_name": "Okafor"},
        {"username": "student.taylor", "first_name": "Taylor", "last_name": "Brooks"},
    ],
    "COSMETOLOGY": [
        {"username": "student.morgan", "first_name": "Morgan", "last_name": "Lee"},
    ],
    "NETWORK-CYBER": [
        {"username": "student.casey", "first_name": "Casey", "last_name": "Reyes"},
    ],
}


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


def username_for(first, last):
    return f"{first.lower()}.{last.lower()}"


async def get_or_create_instructor(
    db, *, first, last, title, phone, school_wide=False
) -> tuple[Instructor, bool]:
    username = username_for(first, last)
    user, _ = await get_or_create_user(
        db,
        username=username,
        defaults=dict(
            email=f"{username}@school.dev",
            password_hash=hash_password("dev-password"),
            first_name=first,
            last_name=last,
            role=UserRole.teacher,
        ),
    )

    result = await db.execute(select(Instructor).where(Instructor.user_id == user.id))
    instructor = result.scalar_one_or_none()
    if instructor is not None:
        return instructor, False

    instructor = Instructor(
        user_id=user.id, title=title, phone=phone, school_wide=school_wide
    )
    db.add(instructor)
    await db.flush()
    return instructor, True


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

        # --- Programs, instructors, instructional assistants ---
        for entry in PROGRAMS:
            program, created = await get_or_create_program(
                db, code=entry["code"], name=entry["name"]
            )
            print(f"{'Created' if created else 'Found'} program: {program.code} ({program.name})")

            for first, last, phone in entry["instructors"]:
                instructor, created = await get_or_create_instructor(
                    db, first=first, last=last, title=TITLE_INSTRUCTOR, phone=phone
                )
                print(f"  {'Created' if created else 'Found'} instructor: {first} {last}")
                if await link_program_instructor(
                    db, program_id=program.id, instructor_id=instructor.id
                ):
                    print(f"  Linked instructor {first} {last} to {program.code}")

            for first, last, phone in entry["assistants"]:
                instructor, created = await get_or_create_instructor(
                    db, first=first, last=last, title=TITLE_ASSISTANT, phone=phone
                )
                print(f"  {'Created' if created else 'Found'} assistant: {first} {last}")
                if await link_program_instructor(
                    db, program_id=program.id, instructor_id=instructor.id
                ):
                    print(f"  Linked assistant {first} {last} to {program.code}")

            for s in PLACEHOLDER_STUDENTS.get(entry["code"], []):
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
                if await enroll_student(db, program_id=program.id, student_id=student.id):
                    print(f"  Enrolled {student.username} in {program.code}")

        # --- Learning support & integration instructors (no program link) ---
        for first, last, title, phone in LEARNING_SUPPORT:
            _, created = await get_or_create_instructor(
                db, first=first, last=last, title=title, phone=phone
            )
            print(f"{'Created' if created else 'Found'} learning support: {first} {last} ({title})")

        for first, last, title, phone in INTEGRATION_INSTRUCTORS:
            _, created = await get_or_create_instructor(
                db, first=first, last=last, title=title, phone=phone, school_wide=True
            )
            print(f"{'Created' if created else 'Found'} integration instructor: {first} {last} ({title})")

        await db.commit()
        print(f"\nSeed complete. Student PIN for login: {default_pin}")


if __name__ == "__main__":
    asyncio.run(seed())
