import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import BeattieLogo from "./BeattieLogo";

// Every link here must be a real route in App.jsx.
const NAV_ITEMS = {
  student: [
    { to: "/student/tasks", label: "My Tasks" },
    { to: "/student/hours", label: "My Hours" },
  ],
  teacher: [{ to: "/teacher", label: "My Program" }],
  admin: [{ to: "/admin", label: "Overview" }],
};

function navClass({ isActive }) {
  const base = "px-3 py-2 text-sm font-medium rounded-md";
  return isActive
    ? `${base} bg-brand-50 text-brand-700`
    : `${base} text-gray-600 hover:text-gray-900 hover:bg-gray-100`;
}

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleSignOut() {
    logout();
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-14">
            <div className="flex items-center gap-6">
              <Link to="/" className="flex items-center gap-2 text-lg font-bold text-gray-900">
                <BeattieLogo size={32} />
                <span className="hidden sm:inline">Beattie Journal</span>
              </Link>
              <div className="flex gap-1">
                {NAV_ITEMS[user.role].map((item) => (
                  <NavLink key={item.to} to={item.to} className={navClass}>
                    {item.label}
                  </NavLink>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="hidden sm:inline text-sm text-gray-600">{user.name}</span>
              <button onClick={handleSignOut} className="text-sm text-gray-500 hover:text-gray-700">
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}
