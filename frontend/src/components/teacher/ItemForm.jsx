import { useState } from "react";
import { useT } from "../../i18n";
import { errorMessage } from "../../lib/api";

const inputClass =
  "w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500";

// Title + description form for a project or task, used to create and to
// edit. onSubmit({ title, description }) must return a promise; onDone runs
// when it resolves, the error shows if it rejects. onCancel closes it.
export default function ItemForm({
  initial = { title: "", description: "" },
  titleLabel,
  descriptionLabel,
  submitLabel,
  savingLabel,
  onSubmit,
  onCancel,
}) {
  const t = useT();
  const [title, setTitle] = useState(initial.title);
  const [description, setDescription] = useState(initial.description);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await onSubmit({ title: title.trim(), description: description.trim() });
    } catch (err) {
      setError(errorMessage(err, t));
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        {titleLabel}
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          maxLength={255}
          autoFocus
          className={`mt-1 ${inputClass}`}
        />
      </label>
      <label className="block text-sm font-medium text-gray-700">
        {descriptionLabel}
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={2}
          maxLength={2000}
          className={`mt-1 ${inputClass}`}
        />
      </label>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <div className="flex gap-3">
        <button
          type="submit"
          disabled={saving || !title.trim()}
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {saving ? savingLabel : submitLabel}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50"
        >
          {t("teacher.cancel")}
        </button>
      </div>
    </form>
  );
}
