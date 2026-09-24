import { useEffect, useState } from "react";
import { useT } from "../../i18n";
import api from "../../lib/api";

// School-wide counts and every program's staff and enrollment.
export default function OverviewPage() {
  const t = useT();
  const [overview, setOverview] = useState(null);
  const [programs, setPrograms] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.get("/admin/overview"), api.get("/admin/programs")])
      .then(([overviewRes, programsRes]) => {
        setOverview(overviewRes.data);
        setPrograms(programsRes.data);
      })
      .catch(() => setError(t("admin.loadFailed")));
  }, [t]);

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!overview) return <p className="text-sm text-gray-500">{t("common.loading")}</p>;

  const stats = [
    [t("admin.programs"), overview.programs],
    [t("admin.instructors"), overview.instructors],
    [t("admin.assistants"), overview.assistants],
    [t("admin.students"), overview.students],
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {stats.map(([label, value]) => (
          <div key={label} className="rounded-lg border border-gray-200 bg-white p-4">
            <p className="text-xs font-semibold text-gray-500">{label}</p>
            <p className="mt-1 text-2xl font-bold text-gray-900">{value}</p>
          </div>
        ))}
      </div>

      <section>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">{t("admin.programs")}</h3>
        <div className="rounded-lg border border-gray-200 bg-white divide-y divide-gray-100">
          {programs.map((p) => (
            <div key={p.id} className="flex items-start justify-between gap-4 p-4">
              <div className="min-w-0">
                <p className="font-medium text-gray-900">{p.name}</p>
                <p className="mt-0.5 text-sm text-gray-500">
                  {p.code}
                  {p.instructors.length > 0 && <> &middot; {p.instructors.join(", ")}</>}
                  {p.assistants.length > 0 && <> &middot; {t("admin.aides", { names: p.assistants.join(", ") })}</>}
                </p>
              </div>
              <span className="shrink-0 rounded-full bg-brand-50 px-2.5 py-0.5 text-xs font-medium text-brand-700">
                {t("admin.studentCount", { count: p.student_count })}
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
