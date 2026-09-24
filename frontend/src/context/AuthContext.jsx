import { createContext, useContext, useEffect, useState } from "react";
import api from "../lib/api";
import { useT } from "../i18n";

const AuthContext = createContext(null);

function Notice({ title, body, action }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="max-w-sm text-center">
        <h1 className="text-lg font-semibold text-gray-900">{title}</h1>
        {body && <p className="mt-2 text-sm text-gray-600">{body}</p>}
        {action}
      </div>
    </div>
  );
}

// `user` is { id, name, role, logout_url } from GET /api/auth/me. Sign-in
// happens in Authelia before this app ever loads, so there's no login page:
// if /auth/me fails, the Authelia session is missing, expired, or disabled.
export function AuthProvider({ children }) {
  const t = useT();
  const [user, setUser] = useState(null);
  const [problem, setProblem] = useState(null);

  useEffect(() => {
    api
      .get("/auth/me")
      .then(({ data }) => setUser(data))
      .catch((error) => setProblem(error.response?.data?.detail ?? "network"));
  }, []);

  if (problem === "account_disabled") {
    return <Notice title={t("auth.disabledTitle")} body={t("auth.disabledBody")} />;
  }
  if (problem === "not_signed_in") {
    return (
      <Notice
        title={t("auth.notSignedInTitle")}
        body={t("auth.notSignedInBody")}
        action={
          // A full reload goes back through Caddy, which sends them to Authelia.
          <button
            onClick={() => window.location.reload()}
            className="mt-4 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
          >
            {t("auth.signIn")}
          </button>
        }
      />
    );
  }
  if (problem) return <Notice title={t("auth.loadFailed")} />;
  if (!user) return <Notice title={t("common.loading")} />;

  return <AuthContext.Provider value={{ user }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
