import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  css: {
    modules: {
      localsConvention: 'camelCase'
    }
  },
  server: {
    host: true,
    port: 3000,
    strictPort: true,
    cors: true,
    allowedHosts: ['all'],
    proxy: {
      '/api': {
        target: 'http://localhost:8003',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  preview: {
    host: true,
    port: 5173,
    strictPort: true,
    allowedHosts: ['all']
  },
  base: '/',
  build: {
    cssMinify: true,
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    },
    sourcemap: true,
    chunkSizeWarningLimit: 1000
  }
})
