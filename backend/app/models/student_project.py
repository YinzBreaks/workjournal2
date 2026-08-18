from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class StudentProject(Base):
    __tablename__ = "student_projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    project: Mapped["Project"] = relationship(back_populates="student_projects")
    student: Mapped["User"] = relationship()
    assignments: Mapped[list["Assignment"]] = relationship(
        back_populates="student_project", cascade="all, delete-orphan"
    )
    work_logs: Mapped[list["WorkLog"]] = relationship(
        back_populates="student_project"
    )


from app.models.project import Project  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.task import Assignment  # noqa: E402
from app.models.worklog import WorkLog  # noqa: E402
