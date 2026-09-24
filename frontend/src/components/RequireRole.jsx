import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

// Signed-in users on a page for another role go home. The API enforces
// the same rules; this only keeps people off pages that would 403.
export default function RequireRole({ roles }) {
  const { user } = useAuth();
  if (!roles.includes(user.role)) return <Navigate to="/" replace />;
  return <Outlet />;
}
