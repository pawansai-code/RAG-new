/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#1d4ed8", // Tailwind blue-700
        secondary: "#3b82f6", // Tailwind blue-500
        background: "#f8fafc", // Tailwind slate-50
        surface: "#ffffff",
        textPrimary: "#1e293b", // Tailwind slate-800
        textSecondary: "#64748b", // Tailwind slate-500
        border: "#e2e8f0" // Tailwind slate-200
      }
    },
  },
  plugins: [],
}
