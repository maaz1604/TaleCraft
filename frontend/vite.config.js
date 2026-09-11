import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

// https://vite.dev/config/
export default defineConfig((command, mode) => {
  // eslint-disable-next-line no-undef
  const env = loadEnv(mode, process.cwd(), "")

  console.log(env.VITE_DEBUG)
  return {
    plugins: [react()],
    server: {
      ...(env.VITE_DEBUG === "true" && {
        proxy: {
          "/api": {
            target: env.VITE_API_BASE_URL?.replace(/\/api\/?$/, "") || "http://localhost:8000",
            changeOrigin: true,
            secure: false,
          },
        },
      }),
    },
  };
});
