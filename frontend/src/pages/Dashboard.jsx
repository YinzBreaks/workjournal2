import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { role } = useAuth();

  switch (role) {
    case "admin":
      return <Navigate to="/admin" replace />;
    case "teacher":
      return <Navigate to="/teacher" replace />;
    case "student":
      return <Navigate to="/student" replace />;
    default:
      return (
        <div className="p-8 text-center">
          <p className="text-gray-600">Unknown role. Contact an administrator.</p>
        </div>
      );
  }
}
