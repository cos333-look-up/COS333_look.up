/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./static_files/**/*.{html,js}",
    "./src/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        'offwhite': '#fffaee'
      },
    },

  },
  plugins: [],
}
