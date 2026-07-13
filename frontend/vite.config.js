// vite.config.js — Vite build tool configuration
// Docs: https://vitejs.dev/config/

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [
    vue()  // enables .vue Single File Component support
  ],

  server: {
    port: 5173,  // frontend runs on http://localhost:5173

    // Proxy: any request to /api/* gets forwarded to the Flask backend.
    // This means the frontend doesn't need to know the backend URL at all.
    proxy: {
      '/api': {
        target: 'http://localhost:5000',   // Flask backend
        changeOrigin: true,
      }
    }
  }
})
