import { useI18n } from "../../i18n";
import { formatMinutes } from "../../lib/format";

// Enrolled students and their total logged hours in this program.
export default function RosterTable({ roster }) {
  const { locale, t } = useI18n();
  return (
    <section>
      <h3 className="text-lg font-semibold text-gray-900 mb-3">{t("teacher.students", { count: roster.length })}</h3>
      <div className="rounded-lg border border-gray-200 bg-white divide-y divide-gray-100">
        {roster.length === 0 && <p className="p-4 text-sm text-gray-500">{t("teacher.noStudents")}</p>}
        {roster.map((student) => (
          <div key={student.id} className="flex items-center justify-between p-3 text-sm">
            <span className="text-gray-900">{student.name}</span>
            <span className="tabular-nums text-gray-600">
              {t("teacher.logged", { time: formatMinutes(student.total_minutes, locale) })}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
