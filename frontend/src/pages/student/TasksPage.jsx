import { useEffect, useState } from "react";
import { useT } from "../../i18n";
import api, { errorMessage } from "../../lib/api";
import { emitHubEvent } from "../../lib/hub";
import AssignmentCard from "../../components/student/AssignmentCard";

// One task on screen at a time (progressive disclosure), starting at the
// first one that isn't complete. Previous/Next step through the rest.
export default function TasksPage() {
  const t = useT();
  const [assignments, setAssignments] = useState([]);
  const [index, setIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/assignments")
      .then(({ data }) => {
        setAssignments(data);
        const firstOpen = data.findIndex((a) => a.status !== "complete");
        setIndex(firstOpen === -1 ? 0 : firstOpen);
      })
      .catch(() => setError(t("tasks.loadFailed")))
      .finally(() => setLoading(false));
  }, [t]);

  async function moveTo(assignmentId, status) {
    setError("");
    try {
      const { data } = await api.patch(`/assignments/${assignmentId}`, { status });
      setAssignments((prev) => prev.map((a) => (a.id === data.id ? data : a)));
      if (status === "complete") {
        emitHubEvent("journal.entry_submitted", {
          contentId: `assignment-${data.id}`,
          title: data.task_title,
        });
      }
    } catch (err) {
      setError(errorMessage(err, t));
    }
  }

  if (loading) return <p className="text-sm text-gray-500">{t("common.loading")}</p>;

  if (assignments.length === 0) {
    return (
      <div className="text-center py-16">
        {error ? (
          <p className="text-sm text-red-600">{error}</p>
        ) : (
          <>
            <p className="text-gray-600">{t("tasks.empty")}</p>
            <p className="text-sm text-gray-500 mt-1">{t("tasks.emptyHint")}</p>
          </>
        )}
      </div>
    );
  }

  const current = assignments[index];
  const navButton =
    "rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-40";

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="flex items-baseline justify-between gap-4">
        <h2 className="text-xl font-semibold text-gray-900">{t("tasks.title")}</h2>
        <p className="text-sm text-gray-500">
          {t("tasks.position", { current: index + 1, total: assignments.length })}
        </p>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <AssignmentCard key={current.id} assignment={current} onMove={moveTo} />

      <div className="flex justify-between">
        <button onClick={() => setIndex(index - 1)} disabled={index === 0} className={navButton}>
          {t("tasks.previous")}
        </button>
        <button
          onClick={() => setIndex(index + 1)}
          disabled={index === assignments.length - 1}
          className={navButton}
        >
          {t("tasks.next")}
        </button>
      </div>
    </div>
  );
}
