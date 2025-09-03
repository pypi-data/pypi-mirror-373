import { defineConfig } from 'vite'

export default defineConfig({
  server: {
      host: '0.0.0.0',
      port: 3000,
      allowedHosts: ['.kavia.ai'],
      headers: {
          'Access-Control-Allow-Origin': '*'
      },
      watch: {
          usePolling: true
      }
  }
})
