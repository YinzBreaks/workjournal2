import { useEffect, useState } from "react";
import api, { errorMessage } from "../../lib/api";

const inputClass =
  "w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500 disabled:bg-gray-100";

// Program -> student -> 4-digit PIN. Calls onToken(accessToken) on success.
export default function StudentPinForm({ onToken }) {
  const [programs, setPrograms] = useState([]);
  const [students, setStudents] = useState([]);
  const [programId, setProgramId] = useState("");
  const [studentId, setStudentId] = useState("");
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api
      .get("/programs")
      .then(({ data }) => setPrograms(data))
      .catch(() => setError("Couldn't load programs. Refresh to try again."));
  }, []);

  async function chooseProgram(id) {
    setProgramId(id);
    setStudentId("");
    setStudents([]);
    if (!id) return;
    try {
      const { data } = await api.get(`/programs/${id}/students`);
      setStudents(data);
    } catch {
      setError("Couldn't load students for that program.");
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const { data } = await api.post("/auth/pin", { student_id: Number(studentId), pin });
      await onToken(data.access_token);
    } catch (err) {
      setError(errorMessage(err, "Sign in failed. Try again."));
      setPin("");
      setSubmitting(false);
    }
  }

  const noStudents = programId && students.length === 0;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="program" className="block text-sm font-medium text-gray-700 mb-1">
          Program
        </label>
        <select
          id="program"
          value={programId}
          onChange={(e) => chooseProgram(e.target.value)}
          required
          className={inputClass}
        >
          <option value="">Select your program...</option>
          {programs.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="student" className="block text-sm font-medium text-gray-700 mb-1">
          Your name
        </label>
        <select
          id="student"
          value={studentId}
          onChange={(e) => setStudentId(e.target.value)}
          required
          disabled={!programId || noStudents}
          className={inputClass}
        >
          <option value="">{noStudents ? "No students in this program yet" : "Select your name..."}</option>
          {students.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="pin" className="block text-sm font-medium text-gray-700 mb-1">
          PIN
        </label>
        <input
          id="pin"
          type="password"
          inputMode="numeric"
          autoComplete="off"
          maxLength={4}
          value={pin}
          onChange={(e) => setPin(e.target.value.replace(/\D/g, "").slice(0, 4))}
          required
          placeholder="4-digit PIN"
          className={`${inputClass} tracking-widest text-center`}
        />
      </div>

      {error && <p className="text-sm text-red-600 text-center">{error}</p>}

      <button
        type="submit"
        disabled={submitting || !studentId || pin.length !== 4}
        className="w-full rounded-lg bg-brand-600 px-4 py-3 text-sm font-medium text-white shadow-sm hover:bg-brand-700 disabled:opacity-50"
      >
        {submitting ? "Signing in..." : "Sign in"}
      </button>
    </form>
  );
}
