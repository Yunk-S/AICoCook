<template>
  <div class="app">
    <header>
      <div class="header-container">
        <router-link to="/" class="logo-area">
          <img :src="isDarkTheme ? logoInverted : logoDefault" alt="AI 烹饪助手 Logo" class="logo-img">
          <h1 class="logo-text">{{ $t('app.title') }}</h1>
        </router-link>
        <div class="controls">
          <button @click="toggleTheme" class="theme-toggle">
            {{ isDarkTheme ? '🌞' : '🌙' }}
          </button>
          <button @click="toggleLanguage" class="lang-toggle">
            {{ currentLanguage === 'zh' ? 'EN' : '中文' }}
          </button>
        </div>
      </div>
      <nav>
        <router-link to="/ai-coach">{{ $t('nav.aiNutritionAssistant') }}</router-link>
        <router-link to="/ai-recommend">{{ $t('nav.aiRecommend') }}</router-link>
        <router-link to="/random-recipe">{{ $t('nav.randomRecipe') }}</router-link>
        <router-link to="/limited-conditions">{{ $t('nav.inspirationRecipes') }}</router-link>
        <router-link to="/food-gallery">{{ $t('nav.foodGallery') }}</router-link>
        <router-link to="/my-recipes">{{ $t('nav.myRecipes') }}</router-link>
      </nav>
    </header>
    
    <main :class="{ 'full-width': isFullWidthPage }">
      <router-view v-slot="{ Component, route }">
        <transition name="page" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </main>
    
    <footer>
      <p>{{ $t('app.copyright') }} &copy; {{ new Date().getFullYear() }} | <a href="mailto:yunkun.syk@gmail.com" class="contact-link">{{ $t('app.contactUs') }}</a></p>
    </footer>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import logoDefault from './assets/logo.png'
import logoInverted from './assets/logo_inverted.png'

const { t, locale } = useI18n()
const route = useRoute()

// 检查是否为需要全宽显示的页面
const isFullWidthPage = computed(() => {
  return route.name === 'AiRecommend' || route.name === 'AiCoach'
})

// 主题切换 - 默认暗色模式
const isDarkTheme = ref(localStorage.getItem('theme') !== 'light')

function toggleTheme() {
  isDarkTheme.value = !isDarkTheme.value
  localStorage.setItem('theme', isDarkTheme.value ? 'dark' : 'light')
}

// 语言切换
const currentLanguage = ref(locale.value)

function toggleLanguage() {
  const newLanguage = currentLanguage.value === 'zh' ? 'en' : 'zh'
  locale.value = newLanguage
  currentLanguage.value = newLanguage
  localStorage.setItem('locale', newLanguage)
}

// 监听主题变化以更新document类名
watch(isDarkTheme, (newVal) => {
  if (newVal) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}, { immediate: true })
</script>

<style>
:root {
  --primary-color: #42b983;
  --secondary-color: #35495e;
  --text-color: #333;
  --bg-color: #f8f9fa;
  --header-bg: #ffffff;
  --card-bg: #ffffff;
  --border-color: #eaeaea;
  --hover-color: #f2f2f2;
}

html {
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

html.dark {
  --primary-color: #42b983;
  --secondary-color: #8bbfcc;
  --text-color: #f0f0f0;
  --bg-color: #222;
  --header-bg: #333;
  --card-bg: #2c2c2c;
  --border-color: #444;
  --hover-color: #3a3a3a;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 只为背景色添加主题切换过渡效果 */
body,
header,
footer {
  transition: background-color 0.4s ease,
              background 0.4s ease;
}

body {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: linear-gradient(135deg, var(--bg-color) 0%, rgba(66, 185, 131, 0.02) 100%);
  color: var(--text-color);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  min-height: 100vh;
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

header {
  background: linear-gradient(180deg, var(--header-bg) 0%, rgba(66, 185, 131, 0.01) 100%);
  border-bottom: 1px solid var(--border-color);
  padding: 1rem;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.logo-area {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: inherit;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.logo-area:hover {
  transform: translateY(-2px);
  background-color: rgba(66, 185, 131, 0.05);
}

.logo-img {
  height: 40px;
  margin-right: 10px;
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.logo-area:hover .logo-img {
  transform: rotate(5deg) scale(1.05);
}

.logo-text {
  color: var(--primary-color);
  font-size: 1.8rem;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.logo-area:hover .logo-text {
  text-shadow: 0 2px 8px rgba(66, 185, 131, 0.3);
}

.controls {
  display: flex;
  gap: 1rem;
}

button {
  background: linear-gradient(135deg, var(--primary-color) 0%, #389968 50%, #2d7a54 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
  overflow: hidden;
  font-weight: 600;
  font-size: 0.95rem;
  letter-spacing: 0.3px;
  box-shadow: 0 4px 15px rgba(66, 185, 131, 0.2);
  backdrop-filter: blur(10px);
  background-size: 200% 200%;
  animation: gradientShift 3s ease infinite;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s cubic-bezier(0.25, 0.8, 0.25, 1);
}

button::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  transform: translate(-50%, -50%);
  border-radius: 50%;
}

button:hover::before {
  left: 100%;
}

button:hover::after {
  width: 100px;
  height: 100px;
}

button:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 8px 25px rgba(66, 185, 131, 0.4);
  background: linear-gradient(135deg, #4ac291 0%, #2d7a54 50%, #1e5d40 100%);
  animation: gradientShift 1.5s ease infinite;
}

button:active {
  transform: translateY(-1px) scale(0.98);
  box-shadow: 0 4px 15px rgba(66, 185, 131, 0.3);
  background: linear-gradient(135deg, #389968 0%, #2d7a54 50%, #1e5d40 100%);
}

nav {
  display: flex;
  justify-content: center;
  padding: 1rem 0;
  gap: 2rem;
  flex-wrap: wrap;
}

nav a {
  color: var(--text-color);
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border-bottom: 2px solid transparent;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
  overflow: hidden;
}

nav a::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(66, 185, 131, 0.1), transparent);
  transition: left 0.5s cubic-bezier(0.25, 0.8, 0.25, 1);
}

nav a:hover::before {
  left: 100%;
}

nav a:hover {
  color: var(--primary-color);
  background-color: rgba(66, 185, 131, 0.05);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.15);
}

nav a.router-link-active {
  color: var(--primary-color);
  background-color: rgba(66, 185, 131, 0.1);
  border-bottom-color: var(--primary-color);
  transform: translateY(-1px);
}

main {
  flex: 1;
  width: 100%;
}

/* 默认页面样式 - 有最大宽度限制 */
main:not(.full-width) {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* 全宽页面样式 - 智能推荐页面 */
main.full-width {
  margin: 0;
  padding: 0;
  max-width: none;
}

/* 页面切换动画 */
.page-enter-active {
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.page-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.98);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(1.02);
}

.page-enter-to,
.page-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}

footer {
  background-color: var(--header-bg);
  border-top: 1px solid var(--border-color);
  padding: 1.5rem;
  text-align: center;
  margin-top: auto;
}

/* Element Plus 按钮样式覆盖 - 圆润化和动画效果 */
.el-button {
  border-radius: 18px !important;
  font-weight: 600 !important;
  letter-spacing: 0.3px !important;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
  position: relative !important;
  overflow: hidden !important;
  backdrop-filter: blur(10px) !important;
  background-size: 200% 200% !important;
}

.el-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s cubic-bezier(0.25, 0.8, 0.25, 1);
  z-index: 1;
}

.el-button::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 70%);
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  transform: translate(-50%, -50%);
  border-radius: 50%;
  z-index: 1;
}

.el-button:hover::before {
  left: 100%;
}

.el-button:hover::after {
  width: 120px;
  height: 120px;
}

.el-button > span {
  position: relative;
  z-index: 2;
}

/* 主要按钮样式 */
.el-button--primary {
  background: linear-gradient(135deg, var(--primary-color) 0%, #389968 50%, #2d7a54 100%) !important;
  border: none !important;
  box-shadow: 0 4px 15px rgba(66, 185, 131, 0.25) !important;
  animation: primaryGradientShift 3s ease infinite;
}

@keyframes primaryGradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.el-button--primary:hover {
  transform: translateY(-2px) scale(1.02) !important;
  box-shadow: 0 8px 25px rgba(66, 185, 131, 0.4) !important;
  background: linear-gradient(135deg, #4ac291 0%, #2d7a54 50%, #1e5d40 100%) !important;
  animation: primaryGradientShift 1.5s ease infinite !important;
}

.el-button--primary:active {
  transform: translateY(-1px) scale(0.98) !important;
  box-shadow: 0 4px 15px rgba(66, 185, 131, 0.3) !important;
}

/* 信息按钮样式 */
.el-button--info {
  background: linear-gradient(135deg, #909399 0%, #73767a 50%, #606266 100%) !important;
  border: none !important;
  box-shadow: 0 4px 15px rgba(144, 147, 153, 0.25) !important;
  animation: infoGradientShift 3s ease infinite;
}

@keyframes infoGradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.el-button--info:hover {
  transform: translateY(-2px) scale(1.02) !important;
  box-shadow: 0 8px 25px rgba(144, 147, 153, 0.4) !important;
  background: linear-gradient(135deg, #a6a9ad 0%, #73767a 50%, #606266 100%) !important;
  animation: infoGradientShift 1.5s ease infinite !important;
}

/* 危险按钮样式 */
.el-button--danger {
  background: linear-gradient(135deg, #f56c6c 0%, #f04747 50%, #c53030 100%) !important;
  border: none !important;
  box-shadow: 0 4px 15px rgba(245, 108, 108, 0.25) !important;
  animation: dangerGradientShift 3s ease infinite;
}

@keyframes dangerGradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.el-button--danger:hover {
  transform: translateY(-2px) scale(1.02) !important;
  box-shadow: 0 8px 25px rgba(245, 108, 108, 0.4) !important;
  background: linear-gradient(135deg, #f78a8a 0%, #f04747 50%, #c53030 100%) !important;
  animation: dangerGradientShift 1.5s ease infinite !important;
}

/* 朴素按钮样式 */
.el-button.is-plain {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(10px) !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1) !important;
}

.el-button.is-plain:hover {
  transform: translateY(-2px) scale(1.02) !important;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15) !important;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%) !important;
}

/* 链接按钮样式 */
.el-button--text, .el-button.is-text {
  border-radius: 12px !important;
  padding: 0.5rem 1rem !important;
  position: relative !important;
  overflow: hidden !important;
}

.el-button--text:hover, .el-button.is-text:hover {
  background: linear-gradient(135deg, rgba(66, 185, 131, 0.1) 0%, rgba(66, 185, 131, 0.05) 100%) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.15) !important;
}

/* 大尺寸按钮 */
.el-button--large {
  padding: 1rem 2rem !important;
  font-size: 1.1rem !important;
  border-radius: 22px !important;
}

/* 小尺寸按钮 */
.el-button--small {
  padding: 0.4rem 0.8rem !important;
  font-size: 0.85rem !important;
  border-radius: 14px !important;
}

/* 加载状态 */
.el-button.is-loading {
  animation: loadingPulse 2s ease-in-out infinite !important;
}

@keyframes loadingPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

/* Footer 样式 */
footer {
  text-align: center;
  padding: 2rem 0;
  margin-top: auto;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

footer p {
  margin: 0;
  color: var(--text-color);
  font-size: 0.9rem;
  opacity: 0.8;
}

.contact-link {
  color: var(--primary-color);
  text-decoration: none;
  transition: all 0.3s ease;
  font-weight: 500;
}

.contact-link:hover {
  color: #3aa876;
  text-decoration: underline;
  transform: translateY(-1px);
}

/* 暗色主题下的footer样式 */
.dark footer {
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.3) 0%, rgba(0, 0, 0, 0.1) 100%);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.dark footer p {
  color: #ffffff;
}

.dark .contact-link {
  color: #42b983;
}

.dark .contact-link:hover {
  color: #3aa876;
}
</style> 