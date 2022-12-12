/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./static_files/**/*.{html,js}",
    "./src/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        'offwhite': '#fffaee',
        'light-pton': '#FFE092',
        'dark-pton': '#F4A261',
        'text': '#3C444D',
        'dark-brown': "#352922"
      },
    },

  },
  plugins: [],
}
