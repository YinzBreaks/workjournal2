import { useEffect, useState } from "react";
import api from "../../lib/api";
import { formatDate, formatMinutes } from "../../lib/format";
import HoursForm from "../../components/student/HoursForm";

function newestFirst(a, b) {
  return b.date.localeCompare(a.date) || b.id - a.id;
}

// The student's hours: log new time, see the running total and past entries.
export default function HoursPage() {
  const [logs, setLogs] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.get("/worklogs"), api.get("/programs/mine")])
      .then(([logsRes, programsRes]) => {
        setLogs(logsRes.data);
        setPrograms(programsRes.data);
      })
      .catch(() => setError("Couldn't load your hours. Refresh to try again."))
      .finally(() => setLoading(false));
  }, []);

  async function remove(log) {
    if (!window.confirm(`Delete ${formatMinutes(log.minutes)} on ${formatDate(log.date)}?`)) return;
    setError("");
    try {
      await api.delete(`/worklogs/${log.id}`);
      setLogs((prev) => prev.filter((l) => l.id !== log.id));
    } catch {
      setError("Couldn't delete that entry. Try again.");
    }
  }

  if (loading) return <p className="text-sm text-gray-500">Loading your hours...</p>;

  const totalMinutes = logs.reduce((sum, l) => sum + l.minutes, 0);
  const showProgram = programs.length > 1;

  return (
    <div className="space-y-6">
      <div className="flex items-baseline justify-between gap-4">
        <h2 className="text-xl font-semibold text-gray-900">My Hours</h2>
        <p className="text-sm text-gray-600">
          Total: <span className="font-semibold text-gray-900">{formatMinutes(totalMinutes)}</span>
        </p>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {programs.length > 0 ? (
        <HoursForm
          programs={programs}
          onCreated={(log) => setLogs((prev) => [log, ...prev].sort(newestFirst))}
        />
      ) : (
        <p className="text-sm text-gray-500">You're not enrolled in a program yet, so you can't log hours.</p>
      )}

      <div className="rounded-lg border border-gray-200 bg-white divide-y divide-gray-100">
        {logs.length === 0 && <p className="p-4 text-sm text-gray-500">No hours logged yet.</p>}
        {logs.map((log) => (
          <div key={log.id} className="flex items-start justify-between gap-4 p-4">
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-900">
                {formatDate(log.date)} &middot; {formatMinutes(log.minutes)}
                {showProgram && <span className="font-normal text-gray-500"> &middot; {log.program_name}</span>}
              </p>
              {log.summary && <p className="mt-0.5 text-sm text-gray-600">{log.summary}</p>}
            </div>
            <button
              onClick={() => remove(log)}
              className="shrink-0 text-xs text-gray-400 hover:text-red-600"
            >
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
