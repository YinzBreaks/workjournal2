import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  headers: { "Content-Type": "application/json" },
});

let accessToken = null;
let refreshPromise = null;

export function setAccessToken(token) {
  accessToken = token;
}

export function getAccessToken() {
  return accessToken;
}

export function clearTokens() {
  accessToken = null;
  sessionStorage.removeItem("wj_refresh");
}

export function setRefreshToken(token) {
  sessionStorage.setItem("wj_refresh", token);
}

export function getRefreshToken() {
  return sessionStorage.getItem("wj_refresh");
}

async function refreshAccessToken() {
  const refresh = getRefreshToken();
  if (!refresh) throw new Error("No refresh token");

  const { data } = await axios.post(
    `${import.meta.env.VITE_API_URL || "/api"}/auth/refresh`,
    { refresh_token: refresh }
  );

  setAccessToken(data.access_token);
  if (data.refresh_token) {
    setRefreshToken(data.refresh_token);
  }
  return data.access_token;
}

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;

      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
      }

      try {
        const newToken = await refreshPromise;
        original.headers.Authorization = `Bearer ${newToken}`;
        return api(original);
      } catch {
        clearTokens();
        window.location.href = "/login";
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
