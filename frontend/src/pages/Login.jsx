import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import BeattieLogo from "../components/BeattieLogo";
import StudentPinForm from "../components/login/StudentPinForm";
import StaffLoginForm from "../components/login/StaffLoginForm";

export default function Login() {
  const { user, login } = useAuth();
  const [mode, setMode] = useState("student");

  // Once `login` sets the user, this sends them to their home page.
  if (user) return <Navigate to="/" replace />;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <BeattieLogo size={72} className="mx-auto mb-3" />
          <h1 className="text-3xl font-bold text-gray-900">Beattie Journal</h1>
          <p className="mt-2 text-gray-600">
            {mode === "student" ? "Student sign in" : "Staff sign in"}
          </p>
        </div>

        {mode === "student" ? (
          <StudentPinForm onToken={login} />
        ) : (
          <StaffLoginForm onToken={login} />
        )}

        <button
          type="button"
          onClick={() => setMode(mode === "student" ? "staff" : "student")}
          className="w-full text-sm text-gray-500 hover:text-gray-700"
        >
          {mode === "student" ? "Staff? Sign in with your username" : "Student? Sign in with your PIN"}
        </button>
      </div>
    </div>
  );
}
