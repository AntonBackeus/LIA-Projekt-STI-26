import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    proxy: {
      // Proxy /api requests to the Flask backend
      '/api': 'http://127.0.0.1:5001' // Your Flask server address
    },
  },
})