from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    instructors: Mapped[list["Instructor"]] = relationship(
        secondary="program_instructors", back_populates="programs"
    )
    students: Mapped[list["ProgramStudent"]] = relationship(
        back_populates="program", cascade="all, delete-orphan"
    )
    projects: Mapped[list["Project"]] = relationship(
        back_populates="program", cascade="all, delete-orphan"
    )


class ProgramInstructor(Base):
    __tablename__ = "program_instructors"

    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id", ondelete="CASCADE"), primary_key=True
    )
    instructor_id: Mapped[int] = mapped_column(
        ForeignKey("instructors.id", ondelete="CASCADE"), primary_key=True
    )


class ProgramStudent(Base):
    __tablename__ = "program_students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id", ondelete="CASCADE")
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    program: Mapped["Program"] = relationship(back_populates="students")
    student: Mapped["User"] = relationship(back_populates="program_students")


from app.models.instructor import Instructor  # noqa: E402
from app.models.project import Project  # noqa: E402
from app.models.user import User  # noqa: E402
