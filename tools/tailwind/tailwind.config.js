/* Mirrors the inline tailwind.config the pages used with the Play CDN, so the
   compiled stylesheet is class-for-class identical. Run from the repo root:
   npx --yes tailwindcss@3.4.17 -c tools/tailwind/tailwind.config.js -i tools/tailwind/input.css -o assets/css/tailwind.css --minify */
module.exports = {
  content: ['./*.html', './assets/js/**/*.js', './tools/partials/*.html'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
      },
      colors: {
        brand: {
          abyss: '#01060D',
          dark: '#010913',
          deep: '#04121F',
          base: '#04121F',
          mid: '#0A2036',
          teal: '#0B3A43',
          card: '#07182A',
          accent: '#22D3EE',
          glow: '#67E8F9',
          violet: '#A78BFA',
          warm: '#FF8A5B',
          ink: '#E8F6FF',
          dim: '#9FBCD0',
        },
      },
    },
  },
};
