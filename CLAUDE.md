# Beattie Journal

A work tracker for the A.W. Beattie Career Center CTE programs. Students sign
in with a PIN, move their tasks between Not started / In progress / Complete,
and log hours. Teachers see their program's roster, hours, and task progress,
and tag integration staff (math, science, ELL, engagement) on tasks so
students know who to ask for help. Admins see school-wide counts.

This branch (`claude/beattietech-local`) is the local version for the
beattietech.local network: username/password and PIN sign-in only, no
Microsoft/Entra.

## Run it

Backend (from `backend/`, Python 3.11+, Postgres 16):

    python -m venv .venv && . .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env        # then set SECRET_KEY and the passwords
    alembic upgrade head
    python -m app.seed          # safe to rerun
    uvicorn app.main:app --port 8000

Frontend (from `frontend/`):

    npm install
    npm run dev                 # http://localhost:5173, proxies /api to :8000

After `alembic upgrade`/`downgrade`, restart uvicorn. Pooled connections hold
prepared statements for the old tables and the next request 500s otherwise.

Seeded sign-ins: staff are `first.last` (e.g. `sarah.nolan`) with
`DEFAULT_STAFF_PASSWORD`; admin is `ADMIN_USER`/`ADMIN_PASS`; students pick
their program and name and use `DEFAULT_STUDENT_PIN`. Students, projects, and
hours in `seed_data.py` are placeholders. Staff are the real directory.

## Where things live

Every file has one job. A change should touch as few files as the list below
implies. Usually one backend file, one frontend file, or one of each.

    backend/app/
      models.py         the whole data model (10 tables)
      schemas.py        every request/response shape the frontend sees
      security.py       passwords, tokens, get_current_user, require_role,
                        ensure_program_access
      db.py / config.py engine+session / settings from .env
      main.py           mounts the routers under /api
      routers/
        auth.py         POST /auth/login, POST /auth/pin, GET /auth/me
        programs.py     GET /programs, /programs/mine, /programs/{id}/students,
                        /programs/{id}/roster, /programs/{id}/projects
        assignments.py  GET /assignments (student's own), PATCH /assignments/{id}
        worklogs.py     GET/POST /worklogs, DELETE /worklogs/{id} (student's own)
        tasks.py        GET /support-staff, POST/DELETE /tasks/{id}/support-staff
        admin.py        GET /admin/overview, /admin/programs
      seed.py           loads seed_data.py (logic only)
      seed_data.py      who and what gets seeded (data only)
    backend/alembic/versions/   one migration per schema change

    frontend/src/
      App.jsx                   all routes, and each role's home page
      lib/api.js                axios client, token storage, errorMessage()
      lib/status.js             status order, labels, pill colors
      lib/format.js             formatDate, formatMinutes, todayISO
      context/AuthContext.jsx   current user; login(token), logout()
      components/Layout.jsx     top nav (per-role links) + page shell
      components/RequireRole.jsx  route guard
      components/BeattieLogo.jsx  hand-drawn SVG stand-in for the real logo
      pages/Login.jsx           switches between the two forms below
      components/login/         StudentPinForm, StaffLoginForm
      pages/student/            TasksPage (board), HoursPage
      components/student/       AssignmentCard (one card), HoursForm
      pages/teacher/            ProgramPage
      components/teacher/       RosterTable, TaskRow (with support-staff tagging)
      pages/admin/              OverviewPage

## Data model in one paragraph

A `User` has a `role` (admin, teacher, student). Staff users also have one
`Staff` row with a `kind`: instructor, assistant, learning_support, or
integration. Only integration staff can be tagged on tasks. `Program` links
to staff through `ProgramStaff` and to students through `ProgramStudent`. A
`Project` (a service request, a lab, a client job) belongs to a program and
has ordered `Task`s. An `Assignment` is one student's copy of one task. Its
`status` is the board column. A `WorkLog` is time a student logged against a
program.

## Conventions

- **Relationships load eagerly** (`lazy="joined"` for many-to-one,
  `lazy="selectin"` for collections). Async SQLAlchemy can't lazy-load on
  attribute access, so never add a relationship without a `lazy=` setting.
  After creating a row, `await db.refresh(obj, ["relationship"])` before
  reading its relationships.
- **Authorization lives in the endpoint.** Students may only touch their own
  rows: return 404, not 403, for someone else's. Teachers go through
  `ensure_program_access(db, user, program_id)`. Admins pass everything.
- **Response shapes live in `schemas.py`.** If the frontend needs a new
  field, add it there and to the function that builds it (for example
  `assignment_out` in `routers/assignments.py`).
- **Error messages are for students.** Say what went wrong and what to do,
  in plain words. The frontend shows the server's `detail` string as-is via
  `errorMessage()`.
- **Status values** are defined in `models.AssignmentStatus` and mirrored in
  `frontend/src/lib/status.js`. Change both together.
- **Styling:** Tailwind only. The school maroon is `brand-*` in
  `tailwind.config.js` (`brand-600` is the primary button). No other color
  config, no CSS files beyond `index.css`.
- **Schema changes:** edit `models.py`, then
  `alembic revision --autogenerate -m "..."`, read the generated file, then
  `alembic upgrade head`. New non-null columns on existing tables need a
  `server_default`.

## How to…

- **Add a field to the student task card:** add it to `AssignmentOut` in
  `schemas.py` and `assignment_out()` in `routers/assignments.py`, then render
  it in `components/student/AssignmentCard.jsx`.
- **Add a nav link:** add the route in `App.jsx` and the link in
  `NAV_ITEMS` in `Layout.jsx`. Never add a link without a route.
- **Add a new endpoint:** put it in the router for that resource, protect
  it with `require_role` or `get_current_user`, and return a schema from
  `schemas.py`.

## Backlog (each is one small, self-contained task)

1. Teachers can't create projects, tasks, or assignments yet. Only the seed
   makes them. Add `POST /programs/{id}/projects` and
   `POST /projects/{id}/tasks` (which assigns the task to every enrolled
   student), then a form on `ProgramPage`.
2. Teachers can't see each student's individual hours entries, only totals.
   Add `GET /programs/{id}/worklogs?student_id=`.
3. There's no UI for admins to add users, reset a PIN, or deactivate
   someone (`users.active`). Deactivating signs the user out on their next
   request.
4. PIN sign-in has no rate limiting. A 4-digit PIN can be guessed. Add a
   lockout before this goes past the lab network.
5. Swap `BeattieLogo.jsx` for the real logo file once one is available (put
   it in `frontend/public/` and use an `<img>`).
