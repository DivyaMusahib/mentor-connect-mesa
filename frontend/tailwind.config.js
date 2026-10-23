/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        mesa: {
          bg: '#FAFAFA',
          canvas: '#F4F4F6',
          card: '#FFFFFF',
          ink: '#09090B',
          charcoal: '#18181B',
          muted: '#71717A',
          subtle: '#A1A1AA',
          border: '#E4E4E7',
          borderLight: '#F4F4F5',
          forest: '#065F46',
          forestHover: '#047857',
          forestLight: '#ECFDF5',
          amber: '#B45309',
          amberLight: '#FFFBEB',
        },
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        heading: ['"Plus Jakarta Sans"', 'sans-serif'],
      },
      boxShadow: {
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.04)',
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 4px 12px 0 rgba(0, 0, 0, 0.02)',
        'card-hover': '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 10px 24px -2px rgba(0, 0, 0, 0.04)',
        'dropdown': '0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.03)',
      },
      letterSpacing: {
        tightest: '-0.03em',
        tighter: '-0.02em',
        tight: '-0.01em',
      },
    },
  },
  plugins: [],
}
