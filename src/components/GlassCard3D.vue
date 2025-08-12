<template>
  <div 
    class="glass-card-3d group" 
    @click="handleClick"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
    :style="{ transitionDelay: cardDelay }"
  >
    <div class="glass-card-inner">
      <!-- 玻璃拟态层 - Z层级：25px -->
      <div class="glass-layer"></div>
      
      <!-- 内容区域 - Z层级：26px -->
      <div class="card-content">
        <div class="content-text">
          <span class="card-title">{{ title }}</span>
          <span class="card-description">{{ description }}</span>
        </div>
      </div>
      
      <!-- 底部按钮区域 - Z层级：26px -->
      <div class="bottom-section">
        <div class="cta-wrapper">
          <button class="cta-button">{{ ctaText }}</button>
          <ChevronDownIcon class="cta-icon" />
        </div>
      </div>
      
      <!-- Logo区域的圆圈塔楼 - 完全按照原始代码，确保内切关系 -->
      <div class="logo-burst">
        <div 
          v-for="(circle, index) in logoCircles" 
          :key="index"
          class="circle-layer"
          :style="{
            width: circle.size,
            height: circle.size,
            top: circle.pos,
            right: circle.pos,
            transform: `translate3d(0, 0, ${circle.z})`,
            transitionDelay: circle.delay
          }"
        ></div>
        
        <!-- Logo容器 - 精确按照原始代码位置 -->
        <div class="logo-container">
          <div class="logo-emoji">{{ logoEmoji }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, h } from 'vue'

// SVG图标组件 - 使用渲染函数避免模板编译警告
const ChevronDownIcon = {
  render() {
    return h('svg', {
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '3',
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round'
    }, [
      h('path', { d: 'm6 9 6 6 6-6' })
    ])
  }
}

const props = defineProps({
  title: {
    type: String,
    default: 'AI 营养助手'
  },
  description: {
    type: String,
    default: '与智能助手对话，获取个性化膳食计划、营养建议和菜谱灵感。'
  },
  logoEmoji: {
    type: String,
    default: '🤖'
  },
  ctaText: {
    type: String,
    default: '立即尝试'
  },
  cardDelay: {
    type: String,
    default: '0ms'
  },
  onClick: {
    type: Function,
    default: () => {}
  }
})

// Logo圆圈配置 - 完美内切布局 + 增强塔形3D立体感
const logoCircles = computed(() => [
  { size: '170px', pos: '8px', z: '20px', delay: '0s' },
  { size: '140px', pos: '10px', z: '40px', delay: '0.4s' },
  { size: '110px', pos: '17px', z: '60px', delay: '0.8s' },
  { size: '80px', pos: '23px', z: '80px', delay: '1.2s' }
])

const handleClick = () => {
  props.onClick()
}

const handleMouseEnter = () => {
  // 鼠标进入时的处理逻辑
}

const handleMouseLeave = () => {
  // 鼠标离开时的处理逻辑
}
</script>

<style scoped>
/* 主卡片容器 - 按照原始代码透视设置 */
.glass-card-3d {
  width: 290px;
  height: 260px;
  perspective: 1000px;
  cursor: pointer;
  margin: 20px;
}

/* 卡片内层 - 塔楼结构的基础 */
.glass-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 50px;
  background: linear-gradient(to bottom right, #18181b, #000000);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  transition: all 0.5s ease-in-out;
  transform-style: preserve-3d;
  /* 完全移除任何裁切属性，保持纯净的3D上下文 */
}

/* 3D悬停 - 30度角度 */
.glass-card-3d:hover .glass-card-inner {
  transform: rotate3d(1, 1, 0, 30deg);
  box-shadow: 
    rgba(0,0,0,0.3) 30px 50px 25px -40px,
    rgba(0,0,0,0.1) 0px 25px 30px 0px;
}

/* 玻璃拟态层 - Z轴深度：25px */
.glass-layer {
  position: absolute;
  inset: 2px;
  border-radius: 55px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  border-left: 1px solid rgba(255, 255, 255, 0.2);
  background: linear-gradient(to bottom, rgba(255,255,255,0.3), rgba(255,255,255,0.1));
  backdrop-filter: blur(8px);
  transform-style: preserve-3d;
  transform: translate3d(0, 0, 25px);
}

/* 内容区域 - Z轴深度：26px */
.card-content {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translate3d(0, 0, 26px);
  transform-style: preserve-3d;
}

.content-text {
  padding: 0 28px 30px 28px;
  text-align: left;
  width: 100%;
}

.card-title {
  display: block;
  font-size: 1.15rem;
  font-weight: 900;
  color: white;
  margin: 0;
  line-height: 1.2;
}

.card-description {
  display: block;
  margin-top: 12px;
  font-size: 14px;
  color: #cbd5e1;
  line-height: 1.3;
}

/* 底部按钮区域 - Z轴深度：26px，扩展到全宽 */
.bottom-section {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  transform-style: preserve-3d;
  transform: translate3d(0, 0, 26px);
}

.cta-wrapper {
  display: flex;
  width: 100%;
  cursor: pointer;
  align-items: center;
  justify-content: flex-end;
  transition: all 0.2s ease-in-out;
}

.cta-wrapper:hover {
  transform: translate3d(0, 0, 10px);
}

.cta-button {
  border: none;
  background: none;
  font-size: 12px;
  font-weight: 700;
  color: white;
  cursor: pointer;
  padding: 0;
  margin-right: 4px;
}

.cta-icon {
  width: 16px;
  height: 16px;
  color: white;
  stroke-width: 3;
}

/* Logo圆圈塔楼 - 增强的层次感效果 */
.logo-burst {
  position: absolute;
  top: 0;
  right: 0;
  transform-style: preserve-3d;
}

/* 圆圈层 */
.circle-layer {
  position: absolute;
  aspect-ratio: 1;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  box-shadow: rgba(100,100,111,0.2) -10px 10px 20px 0px;
  transition: all 0.5s ease-in-out;
  transform-style: preserve-3d;
}

/* Logo容器 */
.logo-container {
  position: absolute;
  top: 30px;
  right: 30px;
  width: 50px;
  height: 50px;
  aspect-ratio: 1;
  border-radius: 50%;
  background: white;
  display: grid;
  place-content: center;
  box-shadow: rgba(100,100,111,0.2) -10px 10px 20px 0px;
  transition: all 0.5s ease-in-out;
  transform: translate3d(0, 0, 100px);
  transition-delay: 1.6s;
  transform-style: preserve-3d;
}

/* Logo悬停*/
.glass-card-3d:hover .logo-container {
  transform: translate3d(0, 0, 120px);
}

.logo-emoji {
  font-size: 20px;
  line-height: 1;
}

/* 亮色模式适配 */
:root:not(.dark) .glass-card-inner {
  background: linear-gradient(to bottom right, #f8fafc, #e2e8f0);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
}

:root:not(.dark) .glass-layer {
  background: linear-gradient(to bottom, rgba(255,255,255,0.8), rgba(255,255,255,0.4));
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  border-left: 1px solid rgba(0, 0, 0, 0.1);
}

:root:not(.dark) .card-title {
  color: #0f172a;
}

:root:not(.dark) .card-description {
  color: #64748b;
}

:root:not(.dark) .cta-button {
  color: #0f172a;
}

:root:not(.dark) .cta-icon {
  color: #0f172a;
}

:root:not(.dark) .circle-layer {
  background: rgba(0, 0, 0, 0.1);
  box-shadow: rgba(0,0,0,0.2) -10px 10px 20px 0px;
}

:root:not(.dark) .logo-container {
  background: #0f172a;
  box-shadow: rgba(0,0,0,0.2) -10px 10px 20px 0px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .glass-card-3d {
    width: 100%;
    max-width: 290px;
    margin: 0 auto 20px;
  }
}
</style>