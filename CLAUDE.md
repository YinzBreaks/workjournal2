# Beattie Journal

A work tracker for Michael Lingsch's Network Engineering & Cyber Security
class at A.W. Beattie Career Center. Students work through their tasks one
at a time and log hours. Teachers see the class roster, hours, and task
progress, and tag integration staff (math, science, ELL, engagement) on
tasks so students know who to ask for help.

This branch (`claude/beattietech-local`) runs inside the **beattietech.local**
ecosystem at `https://journal.beattietech.local`, behind Caddy + Authelia,
like every other app there (beattieNetTrack is the reference). No PINs, no
passwords, no Microsoft sign-in. The CTE-wide, school-auth version comes later.

## Ecosystem rules (non-negotiable, shared with the other beattietech apps)

- **Identity comes only from Authelia headers.** Caddy runs forward auth and
  sets `Remote-User`, `Remote-Name`, `Remote-Email`, `Remote-Groups`
  (`backend/app/security.py`, same logic as beattieNetTrack `src/lib/auth.ts`).
  Group `admins` → admin, `teachers` → teacher, anything else → student.
  Never read a user id or role from a body, query, or path.
- **Accounts are created on first visit** (`provisioning.py`). Students are
  enrolled in `CLASS_PROGRAM_CODE` and given every task; teachers are linked
  to it as instructors. Nobody is seeded except integration staff.
  The original PIN/password app lives untouched on
  `claude/workjournal-frontend-scaffold-wxpciw`.
- **Strict input:** every request body extends `StrictIn` (unknown fields →
  422). Bodies over 16 KB → 413. Writes go through `limit_writes`
  (30/min/user).
- **Errors are codes, not English.** Raise helpers from `errors.py`; every
  code must exist as `errors.<code>` in all locale files.
- **i18n:** en, ar, fa, uk are mandatory; ar and fa are RTL. No hardcoded UI
  strings: use `t("key")` from `useT()`/`useI18n()`. Use logical Tailwind
  spacing (`ps-`/`pe-`/`ms-`/`me-`), never `pl-`/`pr-`/`ml-`/`mr-`. Adding a
  language = one new `frontend/src/i18n/locales/<code>.json`.
  `npm run check:i18n` must pass (the Docker build runs it).
- **Calm UI:** students see exactly one task on screen. No loud badges, no
  flashing, no counters shouting at them.
- **Hub events:** `lib/hub.js` posts `journal.*` events to `/api/events`
  (the hub's path; don't create an `/api/events` route here).
- **No credential fallbacks.** Missing `DATABASE_URL` / `JOURNAL_DB_PASSWORD`
  must fail at boot. Never commit `.env`, keys, or tokens.
- **No headless browsers, ever.** Verify with curl, builds, and file checks.

## Run it

Production (on the beattietech.local Docker host, beside the other apps):

    cp .env.example .env        # set JOURNAL_DB_PASSWORD
    docker compose up -d --build

The container joins the external `beattie` network and only `expose`s 8000.
Add a Caddy site block for `journal.beattietech.local` that mirrors your
existing ones: `forward_auth` to Authelia with `copy_headers Remote-User
Remote-Groups Remote-Name Remote-Email`, route `/api/events` to the hub like
the other hosts, and `reverse_proxy beattie-journal:8000` for everything else.
On start the container migrates, seeds the class, then serves.

Local dev (Python 3.11+, Postgres 16):

    cd backend && python -m venv .venv && . .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env        # set DATABASE_URL
    alembic upgrade head && python -m app.seed
    uvicorn app.main:app --port 8000

    cd frontend && npm install
    DEV_REMOTE_USER=casey DEV_REMOTE_GROUPS=students npm run dev

The Vite proxy injects the `DEV_REMOTE_*` values as Authelia headers. Use
`DEV_REMOTE_GROUPS=teachers` or `admins` for the other views. After
`alembic upgrade`/`downgrade`, restart uvicorn.

## Where things live

Every file has one job. A change should usually touch one backend file, one
frontend file, or one of each.

    backend/app/
      config.py         settings from env (DATABASE_URL required)
      db.py             engine + session
      models.py         the whole data model
      schemas.py        every request/response shape; StrictIn base
      errors.py         error-code helpers (not_found, bad_request(code), ...)
      security.py       Authelia headers → Identity → User; require_role,
                        ensure_program_access
      provisioning.py   first-visit account + class enrollment
      ratelimit.py      limit_writes dependency
      main.py           /api routers, body-size limit, serves built frontend
      routers/
        auth.py         GET /auth/me (id, name, role, logout_url)
        programs.py     /programs/mine, /{id}/roster, /{id}/projects
        projects.py     POST /programs/{id}/projects, PATCH/DELETE /projects/{id},
                        POST /projects/{id}/tasks (assigns to every enrolled
                        student), PATCH/DELETE /tasks/{id}  (teachers/admins;
                        editing keeps student progress)
        assignments.py  GET /assignments (own), PATCH /assignments/{id}
        worklogs.py     GET/POST /worklogs, DELETE /worklogs/{id} (own)
        tasks.py        GET /support-staff, POST/DELETE /tasks/{id}/support-staff
        admin.py        GET /admin/overview, /admin/programs
      seed.py           creates the class, integration staff, and (only when
                        the class is brand new) the starter project
      seed_data.py      what gets seeded, plus the full staff directory
    backend/alembic/versions/   one migration per schema change

    frontend/src/
      i18n/index.jsx            I18nProvider, useT, useI18n, LOCALES
      i18n/locales/*.json       one file per language (_meta.name, _meta.dir)
      App.jsx                   routes; each role's home page
      lib/api.js                axios client; errorMessage(err, t)
      lib/hub.js                emitHubEvent(type, payload)
      lib/status.js             status order + pill colors
      lib/format.js             formatDate, formatMinutes (locale-aware)
      context/AuthContext.jsx   loads /auth/me; not-signed-in/disabled screens
      components/Layout.jsx     nav, language picker, Authelia sign-out link
      pages/student/            TasksPage (one task at a time), HoursPage
      components/student/       AssignmentCard, HoursForm
      pages/teacher/            ProgramPage (teachers and admins)
      components/teacher/       RosterTable, TaskRow (view/edit a task),
                                ProjectHeader (view/edit a project),
                                ItemForm (title + description fields),
                                NewItemForm ("+ New ..." button + ItemForm)
      pages/admin/              OverviewPage
    frontend/scripts/check-i18n.mjs   locale key parity check

## Data model in one paragraph

A `User` mirrors an Authelia account (`username`, `display_name`, `email`,
`role`); `active=false` locks someone out of this app only. Staff users also
have a `Staff` row with a `kind`: instructor, assistant, learning_support, or
integration. Only integration staff can be tagged on tasks. `Program` links to
staff via `ProgramStaff` and students via `ProgramStudent`. A `Project`
belongs to a program and has ordered `Task`s. An `Assignment` is one
student's copy of one task; `status` is where it stands. A `WorkLog` is time
a student logged.

## Conventions

- **Relationships load eagerly** (`lazy="joined"` many-to-one,
  `lazy="selectin"` collections). Never add one without `lazy=`. After
  creating a row, `await db.refresh(obj, ["relationship"])` before reading it.
- **Authorization lives in the endpoint.** Students only touch their own
  rows (404, not 403, for anyone else's). Teachers go through
  `ensure_program_access`. Admins pass everything.
- **Status values** live in `models.AssignmentStatus`, `lib/status.js`, and
  `status.*` in every locale. Change all three together.
- **Styling:** Tailwind only; school maroon is `brand-*`.
- **Schema changes:** edit `models.py`, `alembic revision --autogenerate`,
  read the file, `alembic upgrade head`. New non-null columns need a
  `server_default`.

## Backlog (each is one small, self-contained task)

1. Teachers can't reorder tasks within a project (`Task.position`).
2. Teachers see only hour totals. Add a per-student hours view.
3. No UI to deactivate a student (`users.active`).
4. Emit `journal.entry_reviewed` once teachers can review work.
5. Swap `BeattieLogo.jsx` for the real logo file (`frontend/public/`).
