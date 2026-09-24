import { useState } from "react";
import { useT } from "../../i18n";
import api, { errorMessage } from "../../lib/api";
import { STATUSES, STATUS_PILL } from "../../lib/status";

// One task in the teacher view: status counts, plus tagging integration
// staff students can ask for help. onStaffChange(taskId, newStaffList).
export default function TaskRow({ task, supportStaff, onStaffChange }) {
  const t = useT();
  const [adding, setAdding] = useState("");
  const [error, setError] = useState("");

  async function tag(staffId) {
    setError("");
    try {
      const { data } = await api.post(`/tasks/${task.id}/support-staff`, { staff_id: Number(staffId) });
      onStaffChange(task.id, data);
      setAdding("");
    } catch (err) {
      setError(errorMessage(err, t));
    }
  }

  async function untag(staffId) {
    setError("");
    try {
      const { data } = await api.delete(`/tasks/${task.id}/support-staff/${staffId}`);
      onStaffChange(task.id, data);
    } catch (err) {
      setError(errorMessage(err, t));
    }
  }

  const available = supportStaff.filter((s) => !task.support_staff.some((t) => t.id === s.id));

  return (
    <div className="p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-medium text-gray-900">{task.title}</p>
          {task.description && <p className="mt-0.5 text-sm text-gray-500">{task.description}</p>}
        </div>
        <div className="flex shrink-0 gap-2 text-xs font-medium">
          {STATUSES.map((status) => (
            <span key={status} className={`rounded-full px-2 py-0.5 ${STATUS_PILL[status]}`}>
              {t("teacher.statCount", { count: task.stats[status], status: t(`status.${status}`) })}
            </span>
          ))}
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        {task.support_staff.map((staff) => (
          <span
            key={staff.id}
            className="inline-flex items-center gap-1.5 rounded-full bg-brand-50 py-1 ps-2.5 pe-1.5 text-xs font-medium text-brand-700"
          >
            {staff.name} ({staff.title})
            <button
              onClick={() => untag(staff.id)}
              className="flex h-4 w-4 items-center justify-center rounded-full hover:bg-brand-100"
              aria-label={t("teacher.remove", { name: staff.name })}
            >
              &times;
            </button>
          </span>
        ))}

        {available.length > 0 && (
          <>
            <select
              value={adding}
              onChange={(e) => setAdding(e.target.value)}
              aria-label={t("teacher.addHelpFor", { task: task.title })}
              className="rounded-full border border-gray-300 px-2 py-1 text-xs text-gray-600 focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
            >
              <option value="">{t("teacher.getHelp")}</option>
              {available.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.title})
                </option>
              ))}
            </select>
            {adding && (
              <button
                onClick={() => tag(adding)}
                className="text-xs font-medium text-brand-600 hover:text-brand-700"
              >
                {t("teacher.add")}
              </button>
            )}
          </>
        )}
      </div>
      {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
    </div>
  );
}
