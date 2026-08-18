import { createContext, useContext, useState, useEffect, useCallback, useRef } from "react";
import api, {
  setAccessToken,
  getAccessToken,
  clearTokens,
  setRefreshToken,
  getRefreshToken,
} from "../lib/api";

const AuthContext = createContext(null);

function decodeJwtPayload(token) {
  try {
    const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(base64));
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const refreshTimerRef = useRef(null);

  const scheduleRefresh = useCallback((token) => {
    if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current);

    const payload = decodeJwtPayload(token);
    if (!payload?.exp) return;

    const msUntilExpiry = payload.exp * 1000 - Date.now();
    const refreshIn = Math.max(msUntilExpiry - 60_000, 0);

    refreshTimerRef.current = setTimeout(async () => {
      try {
        const { data } = await api.post("/auth/refresh", {
          refresh_token: getRefreshToken(),
        });
        setAccessToken(data.access_token);
        if (data.refresh_token) setRefreshToken(data.refresh_token);

        const newPayload = decodeJwtPayload(data.access_token);
        setUser({
          id: newPayload.sub || newPayload.user_id,
          name: newPayload.name,
          role: newPayload.role,
        });
        scheduleRefresh(data.access_token);
      } catch {
        clearTokens();
        setUser(null);
      }
    }, refreshIn);
  }, []);

  const processTokens = useCallback(
    (accessTokenStr, refreshTokenStr) => {
      setAccessToken(accessTokenStr);
      if (refreshTokenStr) setRefreshToken(refreshTokenStr);

      const payload = decodeJwtPayload(accessTokenStr);
      if (!payload) {
        clearTokens();
        setUser(null);
        return;
      }

      setUser({
        id: payload.sub || payload.user_id,
        name: payload.name,
        role: payload.role,
      });
      scheduleRefresh(accessTokenStr);
    },
    [scheduleRefresh]
  );

  useEffect(() => {
    const existingRefresh = getRefreshToken();
    if (existingRefresh) {
      api
        .post("/auth/refresh", { refresh_token: existingRefresh })
        .then(({ data }) => {
          processTokens(data.access_token, data.refresh_token);
        })
        .catch(() => {
          clearTokens();
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }

    return () => {
      if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current);
    };
  }, [processTokens]);

  const login = useCallback(
    (accessTokenStr, refreshTokenStr) => {
      processTokens(accessTokenStr, refreshTokenStr);
    },
    [processTokens]
  );

  const logout = useCallback(async () => {
    try {
      await api.post("/auth/logout");
    } catch {
      // logout is best-effort
    }
    clearTokens();
    setUser(null);
    if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current);
  }, []);

  const isAuthenticated = !!user && !!getAccessToken();
  const role = user?.role || null;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, role, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
