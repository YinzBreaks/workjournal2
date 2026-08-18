import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(150), unique=True)
    email: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    password_hash: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(150), default="")
    last_name: Mapped[str] = mapped_column(String(150), default="")
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.student)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    preferred_lang: Mapped[str] = mapped_column(String(10), default="en")
    theme: Mapped[str] = mapped_column(String(20), default="dark")

    instructor: Mapped["Instructor | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    program_students: Mapped[list["ProgramStudent"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")
    work_logs: Mapped[list["WorkLog"]] = relationship(
        back_populates="student", foreign_keys="WorkLog.student_id"
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


from app.models.instructor import Instructor  # noqa: E402
from app.models.program import ProgramStudent  # noqa: E402
from app.models.audit import AuditLog  # noqa: E402
from app.models.worklog import WorkLog  # noqa: E402
from app.models.token import RefreshToken  # noqa: E402
