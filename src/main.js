import { createApp } from "vue"
import { createPinia } from "pinia"
import ElementPlus from "element-plus"
import "element-plus/dist/index.css"
import "element-plus/theme-chalk/dark/css-vars.css"
import { createI18n } from "vue-i18n"
import App from "./App.vue"
import router from "./router"

// 导入语言包
import zh from "./locales/zh.js"
import en from "./locales/en.js"

// 创建i18n实例
const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem("locale") || "zh",
  messages: {
    zh,
    en
  },
  silentTranslationWarn: true, // 禁用翻译警告，提高性能
  silentFallbackWarn: true, // 禁用回退警告
  warnHtmlMessage: false // 禁用HTML消息警告
})

// 创建应用实例
const app = createApp(App)

// 使用插件
app.use(createPinia())
app.use(router)
app.use(ElementPlus, {
  // 按需加载，减少初始包大小
  size: 'default',
  zIndex: 3000,
})
app.use(i18n)

// 设置全局错误处理器
app.config.errorHandler = (err, vm, info) => {
  console.error('应用错误:', err, info)
}

// 设置性能配置
if (import.meta.env.DEV) {
  app.config.performance = true
}

// 挂载应用
app.mount("#app")
