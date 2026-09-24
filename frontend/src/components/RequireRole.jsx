import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

// Signed-out users go to /login; signed-in users on the wrong page go home.
export default function RequireRole({ roles }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (!roles.includes(user.role)) return <Navigate to="/" replace />;
  return <Outlet />;
}
