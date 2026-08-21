from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Instructor(Base):
    __tablename__ = "instructors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    entra_oid: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    entra_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    user: Mapped["User"] = relationship(back_populates="instructor")
    programs: Mapped[list["Program"]] = relationship(
        secondary="program_instructors", back_populates="instructors"
    )


from app.models.user import User  # noqa: E402
from app.models.program import Program  # noqa: E402
