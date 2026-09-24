import { useState } from "react";
import { useI18n } from "../../i18n";
import { formatDate } from "../../lib/format";

// Buttons shown for each status: [label key, status it moves to, primary?].
const MOVES = {
  not_started: [["tasks.start", "in_progress", true]],
  in_progress: [
    ["tasks.backToNotStarted", "not_started", false],
    ["tasks.markComplete", "complete", true],
  ],
  complete: [["tasks.reopen", "in_progress", false]],
};

const PRIMARY =
  "rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50";
const SECONDARY =
  "rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50";

// The one task on the student's screen. onMove(assignmentId, newStatus).
export default function AssignmentCard({ assignment, onMove }) {
  const { locale, t } = useI18n();
  const [busy, setBusy] = useState(false);

  async function move(status) {
    setBusy(true);
    await onMove(assignment.id, status);
    setBusy(false);
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6">
      <p className="text-sm text-gray-500">
        {assignment.project_title} &middot; {t(`status.${assignment.status}`)}
      </p>
      <h3 className="mt-2 text-xl font-semibold text-gray-900">{assignment.task_title}</h3>
      {assignment.task_description && (
        <p className="mt-2 text-gray-600">{assignment.task_description}</p>
      )}
      {assignment.due_date && assignment.status !== "complete" && (
        <p className="mt-2 text-sm text-gray-500">
          {t("tasks.due", { date: formatDate(assignment.due_date, locale) })}
        </p>
      )}

      {assignment.support_staff.map((staff) => (
        <p key={staff.id} className="mt-3 text-sm text-brand-700">
          {t("tasks.askFor", { name: staff.name, title: staff.title })}
        </p>
      ))}

      <div className="mt-6 flex flex-wrap gap-3">
        {MOVES[assignment.status].map(([label, status, primary]) => (
          <button
            key={status}
            onClick={() => move(status)}
            disabled={busy}
            className={primary ? PRIMARY : SECONDARY}
          >
            {t(label)}
          </button>
        ))}
      </div>
    </div>
  );
}
