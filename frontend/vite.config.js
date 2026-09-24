import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, /api is forwarded to the FastAPI server so the browser only ever
// talks to one origin. In production, a reverse proxy does the same job.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
