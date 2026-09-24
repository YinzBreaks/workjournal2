import { useState } from "react";
import { formatDate } from "../../lib/format";

// Buttons shown for each status: [label, status it moves to, primary?].
const MOVES = {
  not_started: [["Start", "in_progress", true]],
  in_progress: [
    ["Not started", "not_started", false],
    ["Mark complete", "complete", true],
  ],
  complete: [["Reopen", "in_progress", false]],
};

const PRIMARY =
  "rounded-md bg-brand-600 px-2.5 py-1 text-xs font-medium text-white hover:bg-brand-700 disabled:opacity-50";
const SECONDARY =
  "rounded-md border border-gray-300 px-2.5 py-1 text-xs font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50";

// One task on the student's board. onMove(assignmentId, newStatus).
export default function AssignmentCard({ assignment, onMove }) {
  const [busy, setBusy] = useState(false);

  async function move(status) {
    setBusy(true);
    await onMove(assignment.id, status);
    setBusy(false);
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-3 shadow-sm">
      <p className="text-xs text-gray-500">
        {assignment.program_name} &middot; {assignment.project_title}
      </p>
      <p className="mt-1 font-medium text-gray-900">{assignment.task_title}</p>
      {assignment.task_description && (
        <p className="mt-0.5 text-sm text-gray-500">{assignment.task_description}</p>
      )}
      {assignment.due_date && assignment.status !== "complete" && (
        <p className="mt-1 text-xs text-gray-400">Due {formatDate(assignment.due_date)}</p>
      )}

      {assignment.support_staff.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {assignment.support_staff.map((staff) => (
            <span
              key={staff.id}
              className="rounded-full bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-700"
            >
              Need help? Ask {staff.name} ({staff.title})
            </span>
          ))}
        </div>
      )}

      <div className="mt-3 flex flex-wrap gap-2">
        {MOVES[assignment.status].map(([label, status, primary]) => (
          <button
            key={status}
            onClick={() => move(status)}
            disabled={busy}
            className={primary ? PRIMARY : SECONDARY}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}
