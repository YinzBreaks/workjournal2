from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class WorkLog(Base):
    __tablename__ = "work_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    student_project_id: Mapped[int | None] = mapped_column(
        ForeignKey("student_projects.id", ondelete="SET NULL"), nullable=True
    )
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )
    date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    minutes: Mapped[int] = mapped_column(Integer)
    summary: Mapped[str] = mapped_column(Text, default="")
    accomplishments: Mapped[str] = mapped_column(Text, default="")
    what_i_learned: Mapped[str] = mapped_column(Text, default="")
    blockers: Mapped[str] = mapped_column(Text, default="")
    links: Mapped[str] = mapped_column(Text, default="")
    evidence_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    student: Mapped["User | None"] = relationship(back_populates="work_logs")
    student_project: Mapped["StudentProject | None"] = relationship(
        back_populates="work_logs"
    )
    project: Mapped["Project | None"] = relationship()


from app.models.user import User  # noqa: E402
from app.models.student_project import StudentProject  # noqa: E402
from app.models.project import Project  # noqa: E402
