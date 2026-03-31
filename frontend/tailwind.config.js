/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        surface: '#FFFFFF',
        shell: '#F5F5F7',
        'text-primary': '#0F172A',
        'text-muted': '#6B7280',
        accent: '#0F766E',
        danger: '#EF4444',
        warning: '#F59E0B',
        success: '#10B981',
      },
      boxShadow: {
        soft: '0 10px 30px rgba(0,0,0,0.05)',
        card: '0 8px 24px rgba(15, 23, 42, 0.06)',
      },
      borderRadius: {
        xl: '16px',
        '2xl': '20px',
      },
      transitionTimingFunction: {
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  },
  plugins: [],
}
