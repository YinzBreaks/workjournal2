"""The whole data model, in one file.

Loading rule: every relationship loads eagerly (many-to-one with a JOIN,
collections with a follow-up SELECT). Async SQLAlchemy can't lazy-load on
attribute access, so this keeps `task.project.program.name` safe anywhere.
Relationships are one-directional unless something actually reads both
sides.
"""

import enum
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"


class StaffKind(str, enum.Enum):
    instructor = "instructor"
    assistant = "assistant"
    learning_support = "learning_support"
    # School-wide support (math, science, ELL, engagement). Only these can
    # be tagged on a task as "ask them for help".
    integration = "integration"


class AssignmentStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    complete = "complete"


class User(Base):
    """Someone who has signed in through Authelia. Created on first visit.

    `username`, `display_name`, `email`, and `role` mirror the Authelia
    headers and are refreshed on every request (see provisioning.py).
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True)
    display_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"))
    # Set false to lock someone out of this app without touching Authelia.
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Staff(Base):
    """A staff member's school role. Every staff member is also a User."""

    __tablename__ = "staff"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    kind: Mapped[StaffKind] = mapped_column(Enum(StaffKind, name="staff_kind"))
    title: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))

    user: Mapped[User] = relationship(lazy="joined")


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(255))

    staff: Mapped[list[Staff]] = relationship(secondary="program_staff", lazy="selectin")


class ProgramStaff(Base):
    __tablename__ = "program_staff"

    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id", ondelete="CASCADE"), primary_key=True
    )
    staff_id: Mapped[int] = mapped_column(
        ForeignKey("staff.id", ondelete="CASCADE"), primary_key=True
    )


class ProgramStudent(Base):
    __tablename__ = "program_students"

    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id", ondelete="CASCADE"), primary_key=True
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )


class Project(Base):
    """A unit of work in a program: a service request, a lab, a client job."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")

    program: Mapped[Program] = relationship(lazy="joined")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    position: Mapped[int] = mapped_column(Integer, default=0)

    project: Mapped[Project] = relationship(lazy="joined")
    support_staff: Mapped[list[Staff]] = relationship(
        secondary="task_support_staff", lazy="selectin"
    )


class TaskSupportStaff(Base):
    __tablename__ = "task_support_staff"

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    )
    staff_id: Mapped[int] = mapped_column(
        ForeignKey("staff.id", ondelete="CASCADE"), primary_key=True
    )


class Assignment(Base):
    """One student's copy of one task. `status` is the column it sits in."""

    __tablename__ = "assignments"
    __table_args__ = (UniqueConstraint("task_id", "student_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[AssignmentStatus] = mapped_column(
        Enum(AssignmentStatus, name="assignment_status"),
        default=AssignmentStatus.not_started,
    )
    due_date: Mapped[date | None] = mapped_column(Date)

    task: Mapped[Task] = relationship(lazy="joined")


class WorkLog(Base):
    """Time a student logged against a program (shop hours, clinic hours)."""

    __tablename__ = "work_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id", ondelete="CASCADE"))
    date: Mapped[date] = mapped_column(Date)
    minutes: Mapped[int] = mapped_column(Integer)
    summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    program: Mapped[Program] = relationship(lazy="joined")
