import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // GoA Design System color tokens
        'goa-blue': {
          DEFAULT: '#0070c0',
          50: '#e8f4fd',
          100: '#b8ddf8',
          200: '#88c6f3',
          300: '#58afee',
          400: '#2898e9',
          500: '#0070c0',
          600: '#005a9a',
          700: '#004373',
          800: '#002d4d',
          900: '#001626',
        },
        'goa-interactive': '#0070c0',
        'goa-emergency': '#d9292b',
        'goa-success': '#006f00',
        'goa-warning': '#feba35',
        'goa-info': '#0070c0',
      },
      fontFamily: {
        'goa': ['acumin-pro-semi-condensed', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config
