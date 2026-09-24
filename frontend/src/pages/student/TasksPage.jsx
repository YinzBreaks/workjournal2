import { useEffect, useState } from "react";
import api from "../../lib/api";
import { STATUSES, STATUS_LABEL } from "../../lib/status";
import AssignmentCard from "../../components/student/AssignmentCard";

// The student's task board: one column per status.
export default function TasksPage() {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/assignments")
      .then(({ data }) => setAssignments(data))
      .catch(() => setError("Couldn't load your tasks. Refresh to try again."))
      .finally(() => setLoading(false));
  }, []);

  async function moveTo(assignmentId, status) {
    setError("");
    try {
      const { data } = await api.patch(`/assignments/${assignmentId}`, { status });
      setAssignments((prev) => prev.map((a) => (a.id === data.id ? data : a)));
    } catch {
      setError("Couldn't move that task. Try again.");
    }
  }

  if (loading) return <p className="text-sm text-gray-500">Loading your tasks...</p>;

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-900">My Tasks</h2>
      {error && <p className="text-sm text-red-600">{error}</p>}

      {assignments.length === 0 && !error ? (
        <div className="text-center py-16">
          <p className="text-gray-600">You don't have any tasks yet.</p>
          <p className="text-sm text-gray-400 mt-1">They'll show up here once your teacher assigns them.</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-3">
          {STATUSES.map((status) => {
            const column = assignments.filter((a) => a.status === status);
            return (
              <section key={status} className="rounded-lg bg-gray-100 p-3">
                <h3 className="flex items-center justify-between text-sm font-semibold text-gray-700">
                  {STATUS_LABEL[status]}
                  <span className="text-xs font-medium text-gray-500">{column.length}</span>
                </h3>
                <div className="mt-3 space-y-3">
                  {column.map((a) => (
                    <AssignmentCard key={a.id} assignment={a} onMove={moveTo} />
                  ))}
                  {column.length === 0 && (
                    <p className="text-xs text-gray-400 text-center py-4">Nothing here</p>
                  )}
                </div>
              </section>
            );
          })}
        </div>
      )}
    </div>
  );
}
