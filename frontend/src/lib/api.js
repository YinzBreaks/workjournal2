import axios from "axios";

// Per-tab session: closing the tab signs the student out, which is what
// you want on a shared lab computer.
const TOKEN_KEY = "bj_token";

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  sessionStorage.removeItem(TOKEN_KEY);
}

// The server's message for a failed request, or `fallback` if it has none.
export function errorMessage(error, fallback) {
  const detail = error?.response?.data?.detail;
  return typeof detail === "string" ? detail : fallback;
}

const api = axios.create({ baseURL: "/api" });

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // A stored token was rejected (expired, or the account was turned off).
    // A failed sign-in has no stored token, so it falls through to the form.
    if (error.response?.status === 401 && getToken()) {
      clearToken();
      window.location.assign("/login");
    }
    return Promise.reject(error);
  }
);

export default api;
