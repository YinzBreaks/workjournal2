/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // A.W. Beattie Career Center brand maroon, replacing the default
        // Tailwind blue used throughout the app's accent color.
        brand: {
          50: "#f8eef0",
          100: "#f0dbe0",
          200: "#ddb0ba",
          300: "#c8838f",
          400: "#a85465",
          500: "#8a3a4c",
          600: "#6b2a3a",
          700: "#551f2c",
          800: "#3f1620",
          900: "#2a0f16",
        },
      },
    },
  },
  plugins: [],
};
