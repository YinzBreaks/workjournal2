import { useEffect, useState } from "react";
import api from "../lib/api";

const STATUS_LABEL = {
  not_started: "Not started",
  in_progress: "In progress",
  complete: "Complete",
};

const STATUS_CLASS = {
  not_started: "bg-gray-100 text-gray-600",
  in_progress: "bg-amber-50 text-amber-700",
  complete: "bg-green-50 text-green-700",
};

export default function StudentDashboard() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/students/me/projects")
      .then(({ data }) => setProjects(data))
      .catch(() => setError("Couldn't load your projects. Try refreshing."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="text-gray-500 text-sm">Loading your projects...</p>;
  }

  if (error) {
    return <p className="text-red-600 text-sm">{error}</p>;
  }

  if (projects.length === 0) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-600">You're not enrolled in any projects yet.</p>
        <p className="text-gray-400 text-sm mt-1">Check back once your teacher assigns one.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {projects.map((project) => (
        <section key={project.id}>
          <div className="mb-3">
            <h3 className="text-lg font-semibold text-gray-900">{project.title}</h3>
            <p className="text-sm text-gray-500">
              {project.program.code} &middot; {project.program.name}
            </p>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100">
            {project.tasks.map((task) => (
              <div key={task.id} className="p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <p className="font-medium text-gray-900">{task.title}</p>
                    <p className="text-sm text-gray-500 mt-0.5">{task.description}</p>
                    {task.assignment?.due_date && (
                      <p className="text-xs text-gray-400 mt-1">
                        Due {task.assignment.due_date}
                      </p>
                    )}
                  </div>
                  <span
                    className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                      STATUS_CLASS[task.assignment?.status] || STATUS_CLASS.not_started
                    }`}
                  >
                    {STATUS_LABEL[task.assignment?.status] || "Not assigned"}
                  </span>
                </div>

                {task.support_staff.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {task.support_staff.map((staff) => (
                      <span
                        key={staff.id}
                        className="inline-flex items-center rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700"
                      >
                        Need help? Ask {staff.name}
                        {staff.title ? ` (${staff.title})` : ""}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
