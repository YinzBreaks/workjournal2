import { Link, NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LOCALES, useI18n } from "../i18n";
import BeattieLogo from "./BeattieLogo";

// Every link here must be a real route in App.jsx. Labels are locale keys.
const NAV_ITEMS = {
  student: [
    { to: "/student/tasks", label: "nav.tasks" },
    { to: "/student/hours", label: "nav.hours" },
  ],
  teacher: [{ to: "/teacher", label: "nav.class" }],
  admin: [
    { to: "/admin", label: "nav.overview" },
    { to: "/teacher", label: "nav.class" },
  ],
};

function navClass({ isActive }) {
  const base = "px-3 py-2 text-sm font-medium rounded-md";
  return isActive
    ? `${base} bg-brand-50 text-brand-700`
    : `${base} text-gray-600 hover:text-gray-900 hover:bg-gray-100`;
}

export default function Layout() {
  const { user } = useAuth();
  const { locale, setLocale, t } = useI18n();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-14">
            <div className="flex items-center gap-6">
              <Link to="/" className="flex items-center gap-2 text-lg font-bold text-gray-900">
                <BeattieLogo size={32} />
                <span className="hidden sm:inline">{t("app.name")}</span>
              </Link>
              <div className="flex gap-1">
                {NAV_ITEMS[user.role].map((item) => (
                  <NavLink key={item.to} to={item.to} end className={navClass}>
                    {t(item.label)}
                  </NavLink>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-4">
              <select
                value={locale}
                onChange={(e) => setLocale(e.target.value)}
                aria-label={t("nav.language")}
                className="rounded-md border-gray-300 py-1 text-sm text-gray-600 focus:border-brand-500 focus:ring-brand-500"
              >
                {Object.entries(LOCALES).map(([code, messages]) => (
                  <option key={code} value={code}>
                    {messages._meta.name}
                  </option>
                ))}
              </select>
              <span className="hidden sm:inline text-sm text-gray-600">{user.name}</span>
              <a href={user.logout_url} className="text-sm text-gray-500 hover:text-gray-700">
                {t("nav.signOut")}
              </a>
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
