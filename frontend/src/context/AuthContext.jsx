import { createContext, useContext, useEffect, useState } from "react";
import api, { clearToken, getToken, setToken } from "../lib/api";

const AuthContext = createContext(null);

// `user` is { id, name, role } from GET /api/auth/me, or null when signed out.
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(() => Boolean(getToken()));

  // Restore a session after a page reload.
  useEffect(() => {
    if (!getToken()) return;
    api
      .get("/auth/me")
      .then(({ data }) => setUser(data))
      .catch(() => clearToken())
      .finally(() => setLoading(false));
  }, []);

  async function login(token) {
    setToken(token);
    try {
      const { data } = await api.get("/auth/me");
      setUser(data);
    } catch (error) {
      clearToken();
      throw error;
    }
  }

  function logout() {
    clearToken();
    setUser(null);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600" />
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>{children}</AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
