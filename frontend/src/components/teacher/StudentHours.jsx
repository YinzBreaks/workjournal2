import { useEffect, useState } from "react";
import { useI18n } from "../../i18n";
import api from "../../lib/api";
import { formatDate, formatMinutes } from "../../lib/format";

// One student's hour entries, shown under their roster row. Read-only.
export default function StudentHours({ programId, studentId }) {
  const { locale, t } = useI18n();
  const [logs, setLogs] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get(`/programs/${programId}/students/${studentId}/worklogs`)
      .then(({ data }) => setLogs(data))
      .catch(() => setError(t("teacher.hoursLoadFailed")));
  }, [programId, studentId, t]);

  if (error) return <p className="px-3 pb-3 text-sm text-red-600">{error}</p>;
  if (!logs) return <p className="px-3 pb-3 text-sm text-gray-500">{t("common.loading")}</p>;
  if (logs.length === 0) {
    return <p className="px-3 pb-3 text-sm text-gray-500">{t("teacher.noHours")}</p>;
  }

  return (
    <ul className="mx-3 mb-3 divide-y divide-gray-100 rounded-md bg-gray-50">
      {logs.map((log) => (
        <li key={log.id} className="p-3 text-sm">
          <p className="font-medium text-gray-900">
            {formatDate(log.date, locale)} &middot; {formatMinutes(log.minutes, locale)}
          </p>
          {log.summary && <p className="mt-0.5 text-gray-600">{log.summary}</p>}
        </li>
      ))}
    </ul>
  );
}
