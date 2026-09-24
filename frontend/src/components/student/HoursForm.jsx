import { useState } from "react";
import { useT } from "../../i18n";
import api, { errorMessage } from "../../lib/api";
import { emitHubEvent } from "../../lib/hub";
import { todayISO } from "../../lib/format";

const inputClass =
  "w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500";

// Log time for one day. onCreated(newLog) after the server saves it.
export default function HoursForm({ programs, onCreated }) {
  const t = useT();
  const [programId, setProgramId] = useState(String(programs[0].id));
  const [date, setDate] = useState(todayISO());
  const [hours, setHours] = useState("");
  const [summary, setSummary] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      const { data } = await api.post("/worklogs", {
        program_id: Number(programId),
        date,
        minutes: Math.round(Number(hours) * 60),
        summary: summary.trim(),
      });
      onCreated(data);
      emitHubEvent("journal.entry_created", { contentId: `worklog-${data.id}`, minutes: data.minutes });
      setHours("");
      setSummary("");
    } catch (err) {
      setError(errorMessage(err, t));
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-lg border border-gray-200 bg-white p-4 space-y-3">
      <div className="grid gap-3 sm:grid-cols-3">
        {programs.length > 1 && (
          <div>
            <label htmlFor="hours-program" className="block text-sm font-medium text-gray-700 mb-1">
              {t("hours.program")}
            </label>
            <select
              id="hours-program"
              value={programId}
              onChange={(e) => setProgramId(e.target.value)}
              className={inputClass}
            >
              {programs.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
        )}
        <div>
          <label htmlFor="hours-date" className="block text-sm font-medium text-gray-700 mb-1">
            {t("hours.date")}
          </label>
          <input
            id="hours-date"
            type="date"
            value={date}
            max={todayISO()}
            onChange={(e) => setDate(e.target.value)}
            required
            className={inputClass}
          />
        </div>
        <div>
          <label htmlFor="hours-amount" className="block text-sm font-medium text-gray-700 mb-1">
            {t("hours.hours")}
          </label>
          <input
            id="hours-amount"
            type="number"
            min="0.25"
            max="12"
            step="0.25"
            value={hours}
            onChange={(e) => setHours(e.target.value)}
            placeholder={t("hours.hoursPlaceholder")}
            required
            className={inputClass}
          />
        </div>
      </div>

      <div>
        <label htmlFor="hours-summary" className="block text-sm font-medium text-gray-700 mb-1">
          {t("hours.summary")}
        </label>
        <textarea
          id="hours-summary"
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
          rows={2}
          maxLength={2000}
          className={inputClass}
        />
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        type="submit"
        disabled={saving}
        className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand-700 disabled:opacity-50"
      >
        {saving ? t("hours.saving") : t("hours.save")}
      </button>
    </form>
  );
}
