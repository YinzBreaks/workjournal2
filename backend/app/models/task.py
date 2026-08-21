import enum
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AssignmentStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    complete = "complete"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    order: Mapped[int] = mapped_column(Integer, default=0)

    project: Mapped["Project"] = relationship(back_populates="tasks")
    assignments: Mapped[list["Assignment"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )
    support_staff: Mapped[list["Instructor"]] = relationship(
        secondary="task_support_staff", back_populates="support_tasks"
    )


class TaskSupportStaff(Base):
    __tablename__ = "task_support_staff"

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    )
    instructor_id: Mapped[int] = mapped_column(
        ForeignKey("instructors.id", ondelete="CASCADE"), primary_key=True
    )


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE")
    )
    student_project_id: Mapped[int] = mapped_column(
        ForeignKey("student_projects.id", ondelete="CASCADE")
    )
    status: Mapped[AssignmentStatus] = mapped_column(
        Enum(AssignmentStatus), default=AssignmentStatus.not_started
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    task: Mapped["Task"] = relationship(back_populates="assignments")
    student_project: Mapped["StudentProject"] = relationship(
        back_populates="assignments"
    )
    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="assignment"
    )


from app.models.project import Project  # noqa: E402
from app.models.student_project import StudentProject  # noqa: E402
from app.models.submission import Submission  # noqa: E402
from app.models.instructor import Instructor  # noqa: E402
