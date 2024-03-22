/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,js,ts,tsx}"],
  theme: {
    colors: {
      transparent: 'transparent',
      current: 'currentColor',
      black: '#000000',
      white: '#ffffff',
      main: '#282c34',
      table: 'rgb(15 23 42)',
      button: 'rgb(148 163 184)',
      transparentDark: 'rgba(0, 0, 0, 0.8);'
    },
    extend: {},
  },
  plugins: [],
}

