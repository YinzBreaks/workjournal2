import { useEffect, useState } from "react";
import api from "../lib/api";

export default function AdminDashboard() {
  const [overview, setOverview] = useState(null);
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.get("/admin/overview"), api.get("/admin/programs")])
      .then(([overviewRes, programsRes]) => {
        setOverview(overviewRes.data);
        setPrograms(programsRes.data);
      })
      .catch(() => setError("Couldn't load the admin overview. Try refreshing."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="text-gray-500 text-sm">Loading...</p>;
  }

  if (error) {
    return <p className="text-red-600 text-sm">{error}</p>;
  }

  const stats = [
    { label: "Programs", value: overview.programs },
    { label: "Instructors", value: overview.instructors },
    { label: "Instructional aides", value: overview.instructional_assistants },
    { label: "Students", value: overview.students },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {stats.map((s) => (
          <div key={s.label} className="bg-white rounded-lg border border-gray-200 p-4">
            <p className="text-xs uppercase tracking-wide text-gray-400 font-semibold">
              {s.label}
            </p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{s.value}</p>
          </div>
        ))}
      </div>

      <section>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Programs</h3>
        <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100">
          {programs.map((p) => (
            <div key={p.id} className="p-4 flex items-start justify-between gap-4">
              <div className="min-w-0">
                <p className="font-medium text-gray-900">{p.name}</p>
                <p className="text-sm text-gray-500 mt-0.5">
                  {p.code}
                  {p.instructors.length > 0 && <> &middot; {p.instructors.join(", ")}</>}
                  {p.assistants.length > 0 && <> &middot; IA: {p.assistants.join(", ")}</>}
                </p>
              </div>
              <span className="shrink-0 rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">
                {p.student_count} student{p.student_count === 1 ? "" : "s"}
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
