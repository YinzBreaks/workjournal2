"""Request and response shapes for the API. Frontend field names come from here."""

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field

from app.models import AssignmentStatus, Staff, UserRole


# --- Auth ---


class MeOut(BaseModel):
    id: int
    name: str
    role: UserRole
    logout_url: str


class StrictIn(BaseModel):
    """Base for every request body: unknown fields are rejected, not ignored."""

    model_config = ConfigDict(extra="forbid")


# --- Shared ---


class ProgramOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class StaffOut(BaseModel):
    id: int
    name: str
    title: str


def staff_out(staff: Staff) -> StaffOut:
    return StaffOut(id=staff.id, name=staff.user.display_name, title=staff.title)


# --- Student: assignments ---


class AssignmentOut(BaseModel):
    id: int
    status: AssignmentStatus
    due_date: dt.date | None
    task_id: int
    task_title: str
    task_description: str
    project_title: str
    program_name: str
    support_staff: list[StaffOut]


class AssignmentUpdateIn(StrictIn):
    status: AssignmentStatus


# --- Student: hours ---


class WorkLogIn(StrictIn):
    program_id: int
    date: dt.date
    minutes: int = Field(ge=1, le=720)
    summary: str = Field(default="", max_length=2000)


class WorkLogOut(BaseModel):
    id: int
    program_id: int
    program_name: str
    date: dt.date
    minutes: int
    summary: str


# --- Teacher ---


class RosterRowOut(BaseModel):
    id: int
    name: str
    total_minutes: int


class TaskStatsOut(BaseModel):
    not_started: int = 0
    in_progress: int = 0
    complete: int = 0


class ProgramTaskOut(BaseModel):
    id: int
    title: str
    description: str
    support_staff: list[StaffOut]
    stats: TaskStatsOut


class ProgramProjectOut(BaseModel):
    id: int
    title: str
    description: str
    tasks: list[ProgramTaskOut]


class TagStaffIn(StrictIn):
    staff_id: int


class ProjectIn(StrictIn):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=2000)


class TaskIn(StrictIn):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=2000)


# --- Admin ---


class OverviewOut(BaseModel):
    programs: int
    instructors: int
    assistants: int
    students: int


class ProgramSummaryOut(BaseModel):
    id: int
    code: str
    name: str
    instructors: list[str]
    assistants: list[str]
    student_count: int
