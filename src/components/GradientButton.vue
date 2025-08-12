<template>
  <button
    :class="[
      'gradient-button',
      variant,
      {
        'gradient-button--disabled': disabled,
        'gradient-button--loading': loading
      }
    ]"
    :disabled="disabled || loading"
    v-bind="$attrs"
    @click="$emit('click', $event)"
  >
    <span class="gradient-button__content">
      <template v-if="loading">
        <span class="gradient-button__spinner"></span>
      </template>
      <slot />
    </span>
  </button>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'default'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
});

defineEmits(['click']);
</script>

<style scoped>
.gradient-button {
  /* 基础形状 */
  border-radius: 11px;
  min-width: 132px;
  padding: 1rem 2.25rem;
  
  /* 字体样式 */
  font-size: 1rem;
  line-height: 19px;
  font-weight: 700;
  font-family: system-ui, -apple-system, sans-serif;
  color: white;
  
  /* 边框样式 */
  border: 2px solid transparent;
  background-clip: padding-box;
  
  /* 过渡效果 - 完全平滑的渐变动画 */
  transition: 
    all 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  
  /* 基础样式 */
  cursor: pointer;
  outline: none;
  position: relative;
  overflow: hidden;
  
  /* 边框变量已移除 - 简化设计 */
  
  /* 默认状态背景 */
  background: radial-gradient(
    ellipse 150% 180.06% at 11.14% 140%,
    #000000 37.35%,
    #08012c 61.36%,
    #4e1e40 78.42%,
    #70464e 89.52%,
    #88394c 100%
  );
  
  /* 发光效果 */
  box-shadow: 
    0 0 20px rgba(136, 57, 76, 0.3),
    0 4px 12px rgba(0, 0, 0, 0.4);
}

/* 悬停状态背景层 */
.gradient-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: inherit;
  opacity: 0;
  background: radial-gradient(
    ellipse 120.24% 103.18% at 0% 91.51%,
    #c96287 0%,
    #c66c64 8.8%,
    #cc7d23 21.44%,
    #37140a 71.34%,
    #000000 85.76%
  );
  transition: opacity 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  z-index: -1;
}

/* 边框渐变效果已移除 - 消除白色线条 */

/* 悬停状态 - 完全平滑的渐变变换 */
.gradient-button:hover {
  /* 增强发光效果 */
  box-shadow: 
    0 0 30px rgba(201, 98, 135, 0.6),
    0 8px 20px rgba(0, 0, 0, 0.3);
  
  transform: translateY(-2px);
}

/* 悬停时显示新背景 */
.gradient-button:hover::before {
  opacity: 1;
}

/* 焦点状态 */
.gradient-button:focus-visible {
  outline: none;
  box-shadow: 
    0 0 0 2px rgba(201, 98, 135, 0.5),
    0 0 30px rgba(201, 98, 135, 0.6),
    0 8px 20px rgba(0, 0, 0, 0.3);
}

/* 禁用状态 */
.gradient-button--disabled {
  opacity: 0.5;
  pointer-events: none;
  cursor: not-allowed;
}

/* 加载状态 */
.gradient-button--loading {
  pointer-events: none;
}

/* 按钮内容 */
.gradient-button__content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  z-index: 1;
  position: relative;
  overflow: hidden;
  width: 100%;
  height: 100%;
}

/* 加载动画 */
.gradient-button__spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 光波效果已移除 - 保持纯净的渐变动画 */

/* 响应式设计 */
@media (max-width: 768px) {
  .gradient-button {
    min-width: 120px;
    padding: 0.875rem 2rem;
    font-size: 0.9rem;
  }
}

/* 暗色模式优化 */
@media (prefers-color-scheme: dark) {
  .gradient-button {
    /* 在暗色模式下增强发光效果 */
    box-shadow: 
      0 0 25px rgba(136, 57, 76, 0.4),
      0 4px 12px rgba(0, 0, 0, 0.6),
      inset 0 1px 0 rgba(255, 255, 255, 0.15);
  }
  
  .gradient-button:hover {
    box-shadow: 
      0 0 35px rgba(201, 98, 135, 0.7),
      0 8px 20px rgba(0, 0, 0, 0.4),
      inset 0 1px 0 rgba(255, 255, 255, 0.25);
  }
}
</style>