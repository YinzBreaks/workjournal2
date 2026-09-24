import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, /api is forwarded to the FastAPI server so the browser only ever
// talks to one origin. In production, Caddy + Authelia sit in front and add
// the Remote-* identity headers.
//
// To act as someone in dev without Authelia, set these before `npm run dev`:
//   DEV_REMOTE_USER=casey DEV_REMOTE_NAME="Casey Reyes" DEV_REMOTE_GROUPS=students
// (use DEV_REMOTE_GROUPS=teachers or admins for the other views).
const devIdentity = process.env.DEV_REMOTE_USER
  ? {
      "Remote-User": process.env.DEV_REMOTE_USER,
      "Remote-Name": process.env.DEV_REMOTE_NAME ?? "",
      "Remote-Groups": process.env.DEV_REMOTE_GROUPS ?? "",
    }
  : {};

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": { target: "http://localhost:8000", headers: devIdentity },
    },
  },
});
