import axios from "axios";

// No tokens: Authelia's session cookie rides along on every request and
// Caddy turns it into identity headers before the API sees it.
const api = axios.create({ baseURL: "/api", withCredentials: true });

// The translated message for a failed request. The API only ever returns
// short codes (backend/app/errors.py), each one a key under "errors".
export function errorMessage(error, t) {
  if (!error?.response) return t("errors.network");
  const code = error.response.data?.detail;
  const key = `errors.${code}`;
  return typeof code === "string" && t(key) !== key ? t(key) : t("errors.generic");
}

export default api;
