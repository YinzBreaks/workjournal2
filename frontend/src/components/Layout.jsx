import { Outlet, Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = {
  admin: [
    { to: "/admin", label: "Dashboard" },
    { to: "/admin/programs", label: "Programs" },
    { to: "/admin/users", label: "Users" },
  ],
  teacher: [
    { to: "/teacher", label: "Dashboard" },
    { to: "/teacher/journals", label: "Journals" },
    { to: "/teacher/students", label: "Students" },
  ],
  student: [
    { to: "/student", label: "Dashboard" },
    { to: "/student/journal", label: "My Journal" },
  ],
};

export default function Layout() {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();

  const navItems = NAV_ITEMS[role] || [];

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-14">
            <div className="flex items-center gap-8">
              <Link to="/" className="text-lg font-bold text-gray-900">
                Beattie Journal
              </Link>
              <div className="hidden sm:flex gap-1">
                {navItems.map((item) => (
                  <Link
                    key={item.to}
                    to={item.to}
                    className="px-3 py-2 text-sm font-medium text-gray-600 rounded-md hover:text-gray-900 hover:bg-gray-100"
                  >
                    {item.label}
                  </Link>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                {user?.name}{" "}
                <span className="inline-flex items-center rounded-full bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-700">
                  {role}
                </span>
              </span>
              <button
                onClick={handleLogout}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
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
