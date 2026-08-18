import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../lib/api";

export default function Login() {
  const { isAuthenticated, login } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode] = useState("choose");
  const [programs, setPrograms] = useState([]);
  const [students, setStudents] = useState([]);
  const [selectedProgram, setSelectedProgram] = useState("");
  const [selectedStudent, setSelectedStudent] = useState("");
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) navigate("/", { replace: true });
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (mode === "student") {
      api.get("/programs").then(({ data }) => setPrograms(data));
    }
  }, [mode]);

  useEffect(() => {
    if (selectedProgram) {
      setSelectedStudent("");
      api
        .get(`/programs/${selectedProgram}/students`)
        .then(({ data }) => setStudents(data));
    }
  }, [selectedProgram]);

  function handleOidcLogin() {
    window.location.href = "/api/auth/oidc/login";
  }

  async function handlePinSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const { data } = await api.post("/auth/student/login", {
        student_id: selectedStudent,
        pin,
      });
      login(data.access_token, data.refresh_token);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">WorkJournal</h1>
          <p className="mt-2 text-gray-600">Sign in to continue</p>
        </div>

        {mode === "choose" && (
          <div className="space-y-4">
            <button
              onClick={handleOidcLogin}
              className="w-full flex items-center justify-center gap-3 rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
            >
              <svg className="h-5 w-5" viewBox="0 0 21 21" fill="none">
                <path d="M0 0h10v10H0z" fill="#f25022" />
                <path d="M11 0h10v10H11z" fill="#7fba00" />
                <path d="M0 11h10v10H0z" fill="#00a4ef" />
                <path d="M11 11h10v10H11z" fill="#ffb900" />
              </svg>
              Sign in with Microsoft
            </button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-gray-50 px-2 text-gray-500">or</span>
              </div>
            </div>

            <button
              onClick={() => setMode("student")}
              className="w-full rounded-lg bg-blue-600 px-4 py-3 text-sm font-medium text-white shadow-sm hover:bg-blue-700"
            >
              Student Sign In
            </button>
          </div>
        )}

        {mode === "student" && (
          <form onSubmit={handlePinSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Program
              </label>
              <select
                value={selectedProgram}
                onChange={(e) => setSelectedProgram(e.target.value)}
                required
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              >
                <option value="">Select a program...</option>
                {programs.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Student
              </label>
              <select
                value={selectedStudent}
                onChange={(e) => setSelectedStudent(e.target.value)}
                required
                disabled={!selectedProgram}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:bg-gray-100"
              >
                <option value="">Select a student...</option>
                {students.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                PIN
              </label>
              <input
                type="password"
                inputMode="numeric"
                maxLength={4}
                pattern="\d{4}"
                value={pin}
                onChange={(e) => setPin(e.target.value.replace(/\D/g, "").slice(0, 4))}
                required
                placeholder="4-digit PIN"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm tracking-widest text-center focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              />
            </div>

            {error && (
              <p className="text-sm text-red-600 text-center">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading || pin.length !== 4}
              className="w-full rounded-lg bg-blue-600 px-4 py-3 text-sm font-medium text-white shadow-sm hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>

            <button
              type="button"
              onClick={() => {
                setMode("choose");
                setError("");
              }}
              className="w-full text-sm text-gray-500 hover:text-gray-700"
            >
              Back
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
