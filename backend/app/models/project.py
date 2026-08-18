from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    program: Mapped["Program"] = relationship(back_populates="projects")
    creator: Mapped["User | None"] = relationship()
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    student_projects: Mapped[list["StudentProject"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


from app.models.program import Program  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.task import Task  # noqa: E402
from app.models.student_project import StudentProject  # noqa: E402
