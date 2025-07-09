import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Couleurs primaires
        primary: {
          DEFAULT: '#667eea',
          dark: '#5a6fd8',
        },
        secondary: '#00d4ff',
        accent: '#ff6b6b',
        
        // Couleurs de fond
        'bg-primary': '#0a0a0f',
        'bg-secondary': '#1a1a2e',
        'bg-tertiary': '#16213e',
        'bg-card': 'rgba(26, 26, 46, 0.8)',
        'bg-glass': 'rgba(255, 255, 255, 0.05)',
        
        // Couleurs de texte
        'text-primary': '#ffffff',
        'text-secondary': '#b8b8b8',
        'text-muted': '#8a8a8a',
        
        // Couleurs de bordure
        'border-light': 'rgba(255, 255, 255, 0.1)',
        'border-medium': 'rgba(255, 255, 255, 0.2)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Poppins', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        'soft': '0 8px 32px rgba(0, 0, 0, 0.3)',
        'strong': '0 16px 64px rgba(0, 0, 0, 0.5)',
        'glow': '0 0 20px rgba(102, 126, 234, 0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-out',
        'slide-in': 'slideIn 0.4s ease-out',
        'pulse': 'pulse 2s infinite',
        'float': 'float 3s ease-in-out infinite',
        'bounce': 'bounce 1s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}

export default config 