import { useState } from "react";
import { useI18n } from "../../i18n";
import { formatMinutes } from "../../lib/format";
import StudentHours from "./StudentHours";

// Enrolled students and their total logged hours in this program. Click a
// student to see their individual entries (one student open at a time).
export default function RosterTable({ programId, roster }) {
  const { locale, t } = useI18n();
  const [openId, setOpenId] = useState(null);

  return (
    <section>
      <h3 className="text-lg font-semibold text-gray-900 mb-3">
        {t("teacher.students", { count: roster.length })}
      </h3>
      <div className="rounded-lg border border-gray-200 bg-white divide-y divide-gray-100">
        {roster.length === 0 && (
          <p className="p-4 text-sm text-gray-500">{t("teacher.noStudents")}</p>
        )}
        {roster.map((student) => {
          const open = openId === student.id;
          return (
            <div key={student.id}>
              <button
                onClick={() => setOpenId(open ? null : student.id)}
                aria-expanded={open}
                className="flex w-full items-center justify-between gap-4 p-3 text-start text-sm hover:bg-gray-50"
              >
                <span className="text-gray-900">
                  <span aria-hidden="true" className="me-2 inline-block w-3 text-gray-400">
                    {open ? "▾" : "▸"}
                  </span>
                  {student.name}
                </span>
                <span className="tabular-nums text-gray-600">
                  {t("teacher.logged", { time: formatMinutes(student.total_minutes, locale) })}
                </span>
              </button>
              {open && <StudentHours programId={programId} studentId={student.id} />}
            </div>
          );
        })}
      </div>
    </section>
  );
}
