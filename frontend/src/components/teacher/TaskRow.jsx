import { useState } from "react";
import { useT } from "../../i18n";
import api, { errorMessage } from "../../lib/api";
import { STATUSES, STATUS_PILL } from "../../lib/status";
import ItemForm from "./ItemForm";

// One task in the teacher view: status counts, plus tagging integration
// staff students can ask for help. onStaffChange(taskId, newStaffList),
// onSave(task, { title, description }) returns a promise, onDelete(task)
// confirms and deletes. onMoveUp / onMoveDown are null at the ends.
export default function TaskRow({
  task,
  supportStaff,
  onStaffChange,
  onSave,
  onDelete,
  onMoveUp,
  onMoveDown,
}) {
  const t = useT();
  const [editing, setEditing] = useState(false);
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

  if (editing) {
    return (
      <div className="p-4">
        <ItemForm
          initial={task}
          titleLabel={t("teacher.taskTitle")}
          descriptionLabel={t("teacher.taskDescription")}
          submitLabel={t("teacher.save")}
          savingLabel={t("teacher.saving")}
          onSubmit={async (fields) => {
            await onSave(task, fields);
            setEditing(false);
          }}
          onCancel={() => setEditing(false)}
        />
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex min-w-0 items-start gap-3">
          <div className="flex shrink-0 flex-col">
            <button
              onClick={onMoveUp}
              disabled={!onMoveUp}
              aria-label={t("teacher.moveUp", { task: task.title })}
              className="rounded px-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-800 disabled:invisible"
            >
              &#9650;
            </button>
            <button
              onClick={onMoveDown}
              disabled={!onMoveDown}
              aria-label={t("teacher.moveDown", { task: task.title })}
              className="rounded px-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-800 disabled:invisible"
            >
              &#9660;
            </button>
          </div>
          <div className="min-w-0">
            <p className="font-medium text-gray-900">{task.title}</p>
            {task.description && (
              <p className="mt-0.5 text-sm text-gray-500">{task.description}</p>
            )}
          </div>
        </div>
        <div className="flex shrink-0 flex-wrap items-center gap-2 text-xs font-medium">
          {STATUSES.map((status) => (
            <span key={status} className={`rounded-full px-2 py-0.5 ${STATUS_PILL[status]}`}>
              {t("teacher.statCount", { count: task.stats[status], status: t(`status.${status}`) })}
            </span>
          ))}
          <button onClick={() => setEditing(true)} className="text-gray-500 hover:text-gray-800">
            {t("teacher.edit")}
          </button>
          <button onClick={() => onDelete(task)} className="text-gray-500 hover:text-red-600">
            {t("teacher.delete")}
          </button>
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
