/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          50: '#f4f7fb',
          100: '#e6edf7',
          200: '#cad7eb',
          300: '#a7b7d7',
          400: '#7a93bc',
          500: '#5672a0',
          600: '#40567e',
          700: '#31415f',
          800: '#212c42',
          900: '#121a2a',
          950: '#08101b',
        },
        mint: '#4ade80',
        sun: '#f59e0b',
        coral: '#fb7185',
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(74, 222, 128, 0.16), 0 18px 50px rgba(8, 16, 27, 0.35)',
      },
      fontFamily: {
        body: ['Manrope', 'Inter', 'Segoe UI', 'sans-serif'],
        display: ['Space Grotesk', 'Manrope', 'sans-serif'],
      },
      backgroundImage: {
        'dashboard-grid': 'radial-gradient(circle at 1px 1px, rgba(148,163,184,0.18) 1px, transparent 0)',
      },
      backgroundSize: {
        grid: '24px 24px',
      },
    },
  },
  plugins: [],
};
