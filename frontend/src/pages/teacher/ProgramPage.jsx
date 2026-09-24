import { useEffect, useState } from "react";
import api from "../../lib/api";
import RosterTable from "../../components/teacher/RosterTable";
import TaskRow from "../../components/teacher/TaskRow";

// A teacher's program: student hours and every task's progress.
export default function ProgramPage() {
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
        setError("Couldn't load your programs. Refresh to try again.");
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (!programId) return;
    setLoading(true);
    Promise.all([api.get(`/programs/${programId}/roster`), api.get(`/programs/${programId}/projects`)])
      .then(([rosterRes, projectsRes]) => {
        setRoster(rosterRes.data);
        setProjects(projectsRes.data);
      })
      .catch(() => setError("Couldn't load this program. Refresh to try again."))
      .finally(() => setLoading(false));
  }, [programId]);

  function updateTaskStaff(taskId, staff) {
    setProjects((prev) =>
      prev.map((p) => ({
        ...p,
        tasks: p.tasks.map((t) => (t.id === taskId ? { ...t, support_staff: staff } : t)),
      }))
    );
  }

  if (!loading && programs.length === 0 && !error) {
    return <p className="text-center py-16 text-gray-600">You're not assigned to a program yet.</p>;
  }

  const program = programs.find((p) => p.id === programId);

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h2 className="text-xl font-semibold text-gray-900">{program?.name ?? "My Program"}</h2>
        {programs.length > 1 && (
          <select
            value={programId ?? ""}
            onChange={(e) => setProgramId(Number(e.target.value))}
            aria-label="Program"
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
        <p className="text-sm text-gray-500">Loading...</p>
      ) : (
        <>
          <RosterTable roster={roster} />

          {projects.length === 0 && (
            <p className="text-sm text-gray-500">No projects in this program yet.</p>
          )}
          {projects.map((project) => (
            <section key={project.id}>
              <h3 className="text-lg font-semibold text-gray-900">{project.title}</h3>
              {project.description && (
                <p className="text-sm text-gray-500 mb-3">{project.description}</p>
              )}
              <div className="rounded-lg border border-gray-200 bg-white divide-y divide-gray-100">
                {project.tasks.map((task) => (
                  <TaskRow
                    key={task.id}
                    task={task}
                    supportStaff={supportStaff}
                    onStaffChange={updateTaskStaff}
                  />
                ))}
              </div>
            </section>
          ))}
        </>
      )}
    </div>
  );
}
