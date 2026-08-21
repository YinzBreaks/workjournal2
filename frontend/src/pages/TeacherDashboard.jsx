import { useEffect, useState, useCallback } from "react";
import api from "../lib/api";

export default function TeacherDashboard() {
  const [programs, setPrograms] = useState([]);
  const [selectedProgramId, setSelectedProgramId] = useState(null);
  const [projects, setProjects] = useState([]);
  const [students, setStudents] = useState([]);
  const [supportStaff, setSupportStaff] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [pendingTag, setPendingTag] = useState({});

  useEffect(() => {
    Promise.all([api.get("/teachers/me/programs"), api.get("/support-staff")])
      .then(([programsRes, staffRes]) => {
        setPrograms(programsRes.data);
        setSupportStaff(staffRes.data);
        if (programsRes.data.length > 0) {
          setSelectedProgramId(programsRes.data[0].id);
        } else {
          setLoading(false);
        }
      })
      .catch(() => {
        setError("Couldn't load your programs. Try refreshing.");
        setLoading(false);
      });
  }, []);

  const loadProgramData = useCallback((programId) => {
    setLoading(true);
    Promise.all([
      api.get(`/programs/${programId}/projects`),
      api.get(`/programs/${programId}/students`),
    ])
      .then(([projectsRes, studentsRes]) => {
        setProjects(projectsRes.data);
        setStudents(studentsRes.data);
      })
      .catch(() => setError("Couldn't load this program's data."))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (selectedProgramId) loadProgramData(selectedProgramId);
  }, [selectedProgramId, loadProgramData]);

  async function addSupportStaff(taskId, instructorId) {
    if (!instructorId) return;
    try {
      await api.post(`/tasks/${taskId}/support-staff`, {
        instructor_id: Number(instructorId),
      });
      loadProgramData(selectedProgramId);
    } catch {
      setError("Couldn't add support staff to that task.");
    }
    setPendingTag((prev) => ({ ...prev, [taskId]: "" }));
  }

  async function removeSupportStaff(taskId, instructorId) {
    try {
      await api.delete(`/tasks/${taskId}/support-staff/${instructorId}`);
      loadProgramData(selectedProgramId);
    } catch {
      setError("Couldn't remove that support staff tag.");
    }
  }

  if (loading && programs.length === 0) {
    return <p className="text-gray-500 text-sm">Loading...</p>;
  }

  if (programs.length === 0) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-600">You're not assigned to any programs yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error && <p className="text-sm text-red-600">{error}</p>}

      {programs.length > 1 && (
        <div className="max-w-xs">
          <label className="block text-sm font-medium text-gray-700 mb-1">Program</label>
          <select
            value={selectedProgramId || ""}
            onChange={(e) => setSelectedProgramId(Number(e.target.value))}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          >
            {programs.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
      )}

      <section>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          Students ({students.length})
        </h3>
        <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100">
          {students.length === 0 && (
            <p className="p-4 text-sm text-gray-500">No students enrolled yet.</p>
          )}
          {students.map((s) => (
            <div key={s.id} className="p-3 text-sm text-gray-900">
              {s.name}
            </div>
          ))}
        </div>
      </section>

      {projects.map((project) => (
        <section key={project.id}>
          <h3 className="text-lg font-semibold text-gray-900 mb-1">{project.title}</h3>
          <p className="text-sm text-gray-500 mb-3">{project.description}</p>

          <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100">
            {project.tasks.map((task) => (
              <div key={task.id} className="p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <p className="font-medium text-gray-900">{task.title}</p>
                    <p className="text-sm text-gray-500 mt-0.5">{task.description}</p>
                  </div>
                  <div className="shrink-0 flex gap-2 text-xs font-medium">
                    <span className="rounded-full bg-gray-100 px-2 py-0.5 text-gray-600">
                      {task.stats.not_started} not started
                    </span>
                    <span className="rounded-full bg-amber-50 px-2 py-0.5 text-amber-700">
                      {task.stats.in_progress} in progress
                    </span>
                    <span className="rounded-full bg-green-50 px-2 py-0.5 text-green-700">
                      {task.stats.complete} complete
                    </span>
                  </div>
                </div>

                <div className="mt-3 flex flex-wrap items-center gap-2">
                  {task.support_staff.map((staff) => (
                    <span
                      key={staff.id}
                      className="inline-flex items-center gap-1.5 rounded-full bg-blue-50 pl-2.5 pr-1.5 py-1 text-xs font-medium text-blue-700"
                    >
                      {staff.name}
                      {staff.title ? ` (${staff.title})` : ""}
                      <button
                        onClick={() => removeSupportStaff(task.id, staff.id)}
                        className="rounded-full hover:bg-blue-100 w-4 h-4 flex items-center justify-center"
                        aria-label={`Remove ${staff.name}`}
                      >
                        &times;
                      </button>
                    </span>
                  ))}

                  <select
                    value={pendingTag[task.id] || ""}
                    onChange={(e) =>
                      setPendingTag((prev) => ({ ...prev, [task.id]: e.target.value }))
                    }
                    className="text-xs rounded-full border border-gray-300 px-2 py-1 text-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="">+ Get help from...</option>
                    {supportStaff
                      .filter((s) => !task.support_staff.some((t) => t.id === s.id))
                      .map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name} ({s.title})
                        </option>
                      ))}
                  </select>
                  {pendingTag[task.id] && (
                    <button
                      onClick={() => addSupportStaff(task.id, pendingTag[task.id])}
                      className="text-xs font-medium text-blue-600 hover:text-blue-700"
                    >
                      Add
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
