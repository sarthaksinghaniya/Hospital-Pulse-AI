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
        shell: '#F8FAFC',
        'text-primary': '#0F172A',
        'text-muted': '#64748B',
        accent: '#2563EB',
        danger: '#EF4444',
        warning: '#F59E0B',
        success: '#10B981',
      },
      boxShadow: {
        soft: '0 4px 20px -2px rgba(0,0,0,0.03), 0 0 3px rgba(0,0,0,0.02)',
        card: '0 8px 30px -4px rgba(15, 23, 42, 0.04), 0 4px 10px -2px rgba(15, 23, 42, 0.02)',
        'card-hover': '0 12px 40px -6px rgba(15, 23, 42, 0.08), 0 6px 15px -3px rgba(15, 23, 42, 0.04)',
      },
      borderRadius: {
        xl: '16px',
        '2xl': '24px',
      },
      transitionTimingFunction: {
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'bouncy': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
    },
  },
  plugins: [],
}
