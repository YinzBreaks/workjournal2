import { useState } from "react";
import { useT } from "../../i18n";
import { errorMessage } from "../../lib/api";

const inputClass =
  "w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500";

// A "+ New ..." button that opens a title/description form. Used for both
// projects and tasks. onSubmit({ title, description }) must return a
// promise; the form closes when it resolves and shows the error if not.
export default function NewItemForm({ openLabel, titleLabel, descriptionLabel, onSubmit }) {
  const t = useT();
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  function close() {
    setOpen(false);
    setTitle("");
    setDescription("");
    setError("");
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await onSubmit({ title: title.trim(), description: description.trim() });
      close();
    } catch (err) {
      setError(errorMessage(err, t));
    } finally {
      setSaving(false);
    }
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="text-sm font-medium text-brand-600 hover:text-brand-700"
      >
        {openLabel}
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
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
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {descriptionLabel}
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={2}
            maxLength={2000}
            className={`mt-1 ${inputClass}`}
          />
        </label>
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <div className="flex gap-3">
        <button
          type="submit"
          disabled={saving || !title.trim()}
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {saving ? t("teacher.creating") : t("teacher.create")}
        </button>
        <button
          type="button"
          onClick={close}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50"
        >
          {t("teacher.cancel")}
        </button>
      </div>
    </form>
  );
}
