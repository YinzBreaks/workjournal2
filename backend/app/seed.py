"""Seed the school's real programs and staff directory for local development.

Source: the school's "Instructors and Learning Support" staff directory.
Student data is NOT real — no roster was provided, and real students'
names aren't something to invent, so a small set of placeholder students
is enrolled in a few real programs just to exercise the login flow.

Usage:
    PYTHONPATH=. python -m app.seed
"""
import asyncio
from datetime import date, timedelta

from sqlalchemy import select

from app.config import get_settings
from app.models import (
    Assignment,
    AssignmentStatus,
    Instructor,
    Program,
    ProgramInstructor,
    ProgramStudent,
    Project,
    StudentProject,
    Task,
    TaskSupportStaff,
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

# One illustrative project per placeholder-student program, with a few
# tasks and per-student assignment status. Some tasks tag an integration
# instructor (by name, looked up against INTEGRATION_INSTRUCTORS) to
# exercise GET /api/support-staff and the task_support_staff join.
PLACEHOLDER_PROJECTS = {
    "AUTO-TECH": {
        "title": "Engine Diagnostics Unit",
        "description": "Diagnose and repair common engine faults using a scan tool.",
        "tasks": [
            {
                "title": "Diagnose OBD-II trouble code",
                "description": "Use the scan tool to pull and interpret a code.",
                "order": 1,
                "support": [("Jen", "Groomes")],
            },
            {
                "title": "Replace brake pads",
                "description": "Remove, inspect, and replace worn brake pads.",
                "order": 2,
                "support": [],
            },
            {
                "title": "Complete fluid service checklist",
                "description": "Inspect and top off all major fluids.",
                "order": 3,
                "support": [],
            },
        ],
        "assignments": {
            "student.alex": {1: "complete", 2: "in_progress", 3: "not_started"},
            "student.jordan": {1: "in_progress", 2: "not_started", 3: "not_started"},
        },
    },
    "CULINARY": {
        "title": "Knife Skills & Mise en Place",
        "description": "Build foundational prep and sanitation skills for service.",
        "tasks": [
            {
                "title": "Complete ServSafe module 1",
                "description": "Read the sanitation module and pass the quiz.",
                "order": 1,
                "support": [("Gretchen", "Boyette")],
            },
            {
                "title": "Plate a 3-course sample menu",
                "description": "Plan and plate an appetizer, entree, and dessert.",
                "order": 2,
                "support": [],
            },
            {
                "title": "Knife skills assessment",
                "description": "Demonstrate julienne, brunoise, and chiffonade cuts.",
                "order": 3,
                "support": [("Nicholas", "Sauer")],
            },
        ],
        "assignments": {
            "student.sam": {1: "complete", 2: "in_progress", 3: "not_started"},
            "student.taylor": {1: "in_progress", 2: "not_started", 3: "not_started"},
        },
    },
    "COSMETOLOGY": {
        "title": "Client Consultation & Cut",
        "description": "Practice consultation, cutting, and color technique.",
        "tasks": [
            {
                "title": "Complete sanitation certification",
                "description": "Pass the state board sanitation exam.",
                "order": 1,
                "support": [],
            },
            {
                "title": "Haircut technique assessment",
                "description": "Demonstrate a graduated bob on a mannequin.",
                "order": 2,
                "support": [],
            },
            {
                "title": "Color theory exam",
                "description": "Written exam on the color wheel and formulation.",
                "order": 3,
                "support": [("Tad", "Thayer")],
            },
        ],
        "assignments": {
            "student.morgan": {1: "complete", 2: "in_progress", 3: "not_started"},
        },
    },
    "NETWORK-CYBER": {
        "title": "Home Lab Network Build",
        "description": "Design, subnet, and secure a small routed network.",
        "tasks": [
            {
                "title": "Build home lab topology diagram",
                "description": "Diagram a routed network with 4 VLANs.",
                "order": 1,
                "support": [("Jen", "Groomes")],
            },
            {
                "title": "Complete Network+ practice exam",
                "description": "Score 80%+ on the practice exam.",
                "order": 2,
                "support": [],
            },
            {
                "title": "Set up a pfSense firewall",
                "description": "Install pfSense and configure basic firewall rules.",
                "order": 3,
                "support": [],
            },
        ],
        "assignments": {
            "student.casey": {1: "complete", 2: "not_started", 3: "not_started"},
        },
    },
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


async def get_or_create_project(db, *, program_id, title, description) -> tuple[Project, bool]:
    result = await db.execute(
        select(Project).where(Project.program_id == program_id, Project.title == title)
    )
    project = result.scalar_one_or_none()
    if project is not None:
        return project, False

    project = Project(program_id=program_id, title=title, description=description)
    db.add(project)
    await db.flush()
    return project, True


async def get_or_create_task(db, *, project_id, title, description, order) -> tuple[Task, bool]:
    result = await db.execute(
        select(Task).where(Task.project_id == project_id, Task.title == title)
    )
    task = result.scalar_one_or_none()
    if task is not None:
        return task, False

    task = Task(project_id=project_id, title=title, description=description, order=order)
    db.add(task)
    await db.flush()
    return task, True


async def get_or_create_student_project(db, *, project_id, student_id) -> tuple[StudentProject, bool]:
    result = await db.execute(
        select(StudentProject).where(
            StudentProject.project_id == project_id,
            StudentProject.student_id == student_id,
        )
    )
    student_project = result.scalar_one_or_none()
    if student_project is not None:
        return student_project, False

    student_project = StudentProject(project_id=project_id, student_id=student_id)
    db.add(student_project)
    await db.flush()
    return student_project, True


async def get_or_create_assignment(
    db, *, task_id, student_project_id, status, due_date
) -> tuple[Assignment, bool]:
    result = await db.execute(
        select(Assignment).where(
            Assignment.task_id == task_id,
            Assignment.student_project_id == student_project_id,
        )
    )
    assignment = result.scalar_one_or_none()
    if assignment is not None:
        return assignment, False

    assignment = Assignment(
        task_id=task_id,
        student_project_id=student_project_id,
        status=status,
        due_date=due_date,
    )
    db.add(assignment)
    await db.flush()
    return assignment, True


async def tag_task_support_staff(db, *, task_id, instructor_id) -> bool:
    result = await db.execute(
        select(TaskSupportStaff).where(
            TaskSupportStaff.task_id == task_id,
            TaskSupportStaff.instructor_id == instructor_id,
        )
    )
    if result.scalar_one_or_none() is not None:
        return False

    db.add(TaskSupportStaff(task_id=task_id, instructor_id=instructor_id))
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

        # --- Illustrative projects/tasks for the placeholder-student programs ---
        for code, proj in PLACEHOLDER_PROJECTS.items():
            result = await db.execute(select(Program).where(Program.code == code))
            program = result.scalar_one()

            project, created = await get_or_create_project(
                db, program_id=program.id, title=proj["title"], description=proj["description"]
            )
            print(f"{'Created' if created else 'Found'} project: {proj['title']} ({code})")

            task_by_order = {}
            for t in proj["tasks"]:
                task, created = await get_or_create_task(
                    db,
                    project_id=project.id,
                    title=t["title"],
                    description=t["description"],
                    order=t["order"],
                )
                task_by_order[t["order"]] = task
                print(f"  {'Created' if created else 'Found'} task: {t['title']}")

                for first, last in t["support"]:
                    result = await db.execute(
                        select(Instructor)
                        .join(User, User.id == Instructor.user_id)
                        .where(User.first_name == first, User.last_name == last)
                    )
                    instructor = result.scalar_one_or_none()
                    if instructor is None:
                        continue
                    if await tag_task_support_staff(
                        db, task_id=task.id, instructor_id=instructor.id
                    ):
                        print(f"  Tagged {first} {last} as support staff on '{t['title']}'")

            for username, statuses in proj["assignments"].items():
                result = await db.execute(select(User).where(User.username == username))
                student = result.scalar_one()

                student_project, created = await get_or_create_student_project(
                    db, project_id=project.id, student_id=student.id
                )
                if created:
                    print(f"  Enrolled {username} in project '{proj['title']}'")

                for order, status_str in statuses.items():
                    task = task_by_order[order]
                    status = AssignmentStatus(status_str)
                    due = (
                        None
                        if status == AssignmentStatus.complete
                        else date.today() + timedelta(days=7)
                    )
                    _, created = await get_or_create_assignment(
                        db,
                        task_id=task.id,
                        student_project_id=student_project.id,
                        status=status,
                        due_date=due,
                    )
                    if created:
                        print(f"  Assigned '{task.title}' to {username} ({status_str})")

        await db.commit()
        print(f"\nSeed complete. Student PIN for login: {default_pin}")


if __name__ == "__main__":
    asyncio.run(seed())
