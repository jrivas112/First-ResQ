import { defineConfig } from 'vite'

export default defineConfig({
  root: '.',
  server: {
    host: '0.0.0.0',
    port: 3000,
    watch: {
      usePolling: true // Important for Docker containers
    },
    hmr: {
      port: 3000
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})
