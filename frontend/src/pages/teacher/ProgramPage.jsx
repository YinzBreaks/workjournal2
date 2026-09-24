import { useEffect, useState } from "react";
import { useT } from "../../i18n";
import api, { errorMessage } from "../../lib/api";
import RosterTable from "../../components/teacher/RosterTable";
import TaskRow from "../../components/teacher/TaskRow";
import NewItemForm from "../../components/teacher/NewItemForm";
import ProjectHeader from "../../components/teacher/ProjectHeader";

// A teacher's program: student hours and every task's progress.
export default function ProgramPage() {
  const t = useT();
  const [programs, setPrograms] = useState([]);
  const [programId, setProgramId] = useState(null);
  const [roster, setRoster] = useState([]);
  const [projects, setProjects] = useState([]);
  const [supportStaff, setSupportStaff] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.get("/programs/mine"), api.get("/support-staff")])
      .then(([programsRes, staffRes]) => {
        setPrograms(programsRes.data);
        setSupportStaff(staffRes.data);
        if (programsRes.data.length > 0) setProgramId(programsRes.data[0].id);
        else setLoading(false);
      })
      .catch(() => {
        setError(t("teacher.loadFailed"));
        setLoading(false);
      });
  }, [t]);

  useEffect(() => {
    if (!programId) return;
    setLoading(true);
    Promise.all([api.get(`/programs/${programId}/roster`), api.get(`/programs/${programId}/projects`)])
      .then(([rosterRes, projectsRes]) => {
        setRoster(rosterRes.data);
        setProjects(projectsRes.data);
      })
      .catch(() => setError(t("teacher.loadFailed")))
      .finally(() => setLoading(false));
  }, [programId, t]);

  function updateTaskStaff(taskId, staff) {
    setProjects((prev) =>
      prev.map((p) => ({
        ...p,
        tasks: p.tasks.map((t) => (t.id === taskId ? { ...t, support_staff: staff } : t)),
      }))
    );
  }

  async function createProject(fields) {
    const { data } = await api.post(`/programs/${programId}/projects`, fields);
    setProjects((prev) => [...prev, data]);
  }

  async function createTask(projectId, fields) {
    const { data } = await api.post(`/projects/${projectId}/tasks`, fields);
    setProjects((prev) =>
      prev.map((p) => (p.id === projectId ? { ...p, tasks: [...p.tasks, data] } : p))
    );
  }

  async function saveProject(project, fields) {
    const { data } = await api.patch(`/projects/${project.id}`, fields);
    setProjects((prev) => prev.map((p) => (p.id === data.id ? { ...p, ...data } : p)));
  }

  async function saveTask(task, fields) {
    const { data } = await api.patch(`/tasks/${task.id}`, fields);
    setProjects((prev) =>
      prev.map((p) => ({
        ...p,
        tasks: p.tasks.map((x) => (x.id === data.id ? { ...x, ...data } : x)),
      }))
    );
  }

  // Swap a task with its neighbour. Shows the new order right away and
  // puts the old one back if the server says no.
  async function moveTask(projectId, index, delta) {
    const before = projects;
    const project = before.find((p) => p.id === projectId);
    const tasks = [...project.tasks];
    [tasks[index], tasks[index + delta]] = [tasks[index + delta], tasks[index]];
    setError("");
    setProjects(before.map((p) => (p.id === projectId ? { ...p, tasks } : p)));
    try {
      await api.put(`/projects/${projectId}/task-order`, { task_ids: tasks.map((x) => x.id) });
    } catch (err) {
      setProjects(before);
      setError(errorMessage(err, t));
    }
  }

  async function deleteProject(project) {
    if (!window.confirm(t("teacher.confirmDeleteProject", { title: project.title }))) return;
    setError("");
    try {
      await api.delete(`/projects/${project.id}`);
      setProjects((prev) => prev.filter((p) => p.id !== project.id));
    } catch (err) {
      setError(errorMessage(err, t));
    }
  }

  async function deleteTask(task) {
    if (!window.confirm(t("teacher.confirmDeleteTask", { title: task.title }))) return;
    setError("");
    try {
      await api.delete(`/tasks/${task.id}`);
      setProjects((prev) =>
        prev.map((p) => ({ ...p, tasks: p.tasks.filter((x) => x.id !== task.id) }))
      );
    } catch (err) {
      setError(errorMessage(err, t));
    }
  }

  if (!loading && programs.length === 0 && !error) {
    return <p className="text-center py-16 text-gray-600">{t("teacher.noProgram")}</p>;
  }

  const program = programs.find((p) => p.id === programId);

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h2 className="text-xl font-semibold text-gray-900">{program?.name ?? t("teacher.fallbackTitle")}</h2>
        {programs.length > 1 && (
          <select
            value={programId ?? ""}
            onChange={(e) => setProgramId(Number(e.target.value))}
            aria-label={t("teacher.program")}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
          >
            {programs.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {loading ? (
        <p className="text-sm text-gray-500">{t("common.loading")}</p>
      ) : (
        <>
          <RosterTable roster={roster} />

          {projects.length === 0 && (
            <p className="text-sm text-gray-500">{t("teacher.noProjects")}</p>
          )}
          {projects.map((project) => (
            <section key={project.id}>
              <ProjectHeader project={project} onSave={saveProject} onDelete={deleteProject} />
              <div className="rounded-lg border border-gray-200 bg-white divide-y divide-gray-100">
                {project.tasks.map((task, index) => (
                  <TaskRow
                    key={task.id}
                    task={task}
                    supportStaff={supportStaff}
                    onStaffChange={updateTaskStaff}
                    onSave={saveTask}
                    onDelete={deleteTask}
                    onMoveUp={index > 0 ? () => moveTask(project.id, index, -1) : null}
                    onMoveDown={
                      index < project.tasks.length - 1
                        ? () => moveTask(project.id, index, 1)
                        : null
                    }
                  />
                ))}
                <div className="p-4">
                  <NewItemForm
                    openLabel={t("teacher.newTask")}
                    titleLabel={t("teacher.taskTitle")}
                    descriptionLabel={t("teacher.taskDescription")}
                    onSubmit={(fields) => createTask(project.id, fields)}
                  />
                </div>
              </div>
            </section>
          ))}

          <div className="rounded-lg border border-dashed border-gray-300 bg-white p-4">
            <NewItemForm
              openLabel={t("teacher.newProject")}
              titleLabel={t("teacher.projectTitle")}
              descriptionLabel={t("teacher.projectDescription")}
              onSubmit={createProject}
            />
          </div>
        </>
      )}
    </div>
  );
}
