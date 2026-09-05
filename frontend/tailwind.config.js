/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        fintech: {
          dark: "#0b0f19",
          card: "#131b2e",
          border: "#1e293b",
          primary: "#3b82f6",
          accent: "#10b981",
          warning: "#f59e0b",
          danger: "#ef4444",
          purple: "#8b5cf6"
        }
      }
    },
  },
  plugins: [],
}
