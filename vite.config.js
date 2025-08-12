import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import fs from 'fs'
import bodyParser from 'body-parser'

const localUserData = () => ({
  name: 'local-user-data',
  configureServer(server) {
    server.middlewares.use(bodyParser.json())
    server.middlewares.use((req, res, next) => {
      if (req.url.startsWith('/api/userdata/')) {
        const file = req.url.split('/').pop()
        const filePath = path.resolve(__dirname, `userdata/${file}.json`)

        if (req.method === 'GET') {
          if (fs.existsSync(filePath)) {
            fs.readFile(filePath, 'utf-8', (err, data) => {
              if (err) {
                res.statusCode = 500
                res.end('Error reading file')
              } else {
                res.setHeader('Content-Type', 'application/json')
                res.end(data)
              }
            })
          } else {
            res.statusCode = 404
            res.end('Not Found')
          }
        } else if (req.method === 'POST') {
          fs.writeFile(filePath, JSON.stringify(req.body, null, 2), (err) => {
            if (err) {
              res.statusCode = 500
              res.end('Error writing file')
            } else {
              res.end('OK')
            }
          })
        } else {
          next()
        }
      } else {
        next()
      }
    })
  }
})

export default defineConfig({
  plugins: [vue(), localUserData()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    host: '0.0.0.0', 
    port: 3001,      // 固定端口
    strictPort: true, // 如果端口被占用，直接退出, 
    cors: true,       
    // 已禁用代理，使用前后端直连
    // proxy: {
    //   // AI教练服务 (FastAPI) -> http://localhost:8000
    //   '/api/v1': {
    //     target: 'http://localhost:8000',
    //     changeOrigin: true,
    //     timeout: 10000, // 超时时间缩短为10秒
    //   },
    //   // RAG智能问答服务 (FastAPI) -> http://localhost:8000
    //   '/api/rag': {
    //     target: 'http://localhost:8000',
    //     changeOrigin: true,
    //     timeout: 10000, // 超时时间缩短为10秒
    //   }
    // }
  },
  assetsInclude: ['**/*.csv'],
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'vue-i18n',
      'element-plus',
      'axios',
      'pinia'
    ],
    exclude: ['body-parser'] 
  },
  esbuild: {
    target: 'es2020'
  },
  cacheDir: 'node_modules/.vite'
})
