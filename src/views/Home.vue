<template>
  <div class="home-page">
    <!-- 背景层：紫色光晕 -->
    <div class="hero-background">
      <div class="radial-gradient"></div>
      <div class="purple-glow"></div>
    </div>
    
    <div class="hero-section">
      <div class="hero-content">

        <!-- 主标题 -->
        <h1 class="hero-title">
          <span class="title-main">{{ t('home.heroTitle') }}</span>
        </h1>
        
        <!-- 副标题 -->
        <p class="hero-subtitle">{{ t('home.heroSubtitle') }}</p>
        
        <!-- CTA 按钮 -->
        <div class="hero-actions">
          <span class="cta-wrapper">
            <span class="cta-border-animation"></span>
            <button class="cta-button" @click="navigateTo('/ai-recommend')">
              {{ t('home.startNow') }}
            </button>
          </span>
        </div>
        

      </div>
    </div>
    
    <div class="features-section" ref="featuresSection">
      <h2 class="section-title">{{ t('home.featuresTitle') }}</h2>
      <p class="section-description">{{ t('home.featuresDescription') }}</p>
      
      <div class="glass-cards-grid">
        <GlassCard3D
          v-for="(feature, index) in featuresData"
          :key="index"
          :title="feature.title"
          :description="feature.description"
          :logo-emoji="feature.emoji"
          :cta-text="feature.ctaText"
          :card-delay="feature.delay"
          :on-click="() => navigateTo(feature.path)"
        />
      </div>
    </div>
    
    <!-- 横向滚动推荐区域 -->
    <recipe-marquee 
      :title="t('home.randomRecipesTitle')"
      :subtitle="t('home.randomRecipesDescription')"
      :duration="40"
      :recipe-count="16"
      @recipe-click="onRecipeClick"
      @favorite-change="onFavoriteChange"
      @view-more="navigateTo('/food-gallery')"
    />
    
    <div class="how-it-works-section">
      <h2 class="section-title">{{ t('home.howItWorksTitle') }}</h2>
      <p class="section-description">{{ t('home.howItWorksDescription') }}</p>
      
      <el-timeline>
        <el-timeline-item 
          v-for="(step, index) in howItWorksSteps" 
          :key="index"
          :timestamp="step.title" 
          placement="top"
          :type="index === howItWorksSteps.length - 1 ? 'success' : 'primary'"
          :hollow="index !== howItWorksSteps.length - 1"
        >
          <el-card class="timeline-card">
            <div class="step-content">
              <div class="step-icon">
                <span>{{ step.emoji }}</span>
              </div>
              <div class="step-text">
                <h3 class="step-title">{{ step.title }}</h3>
                <p class="step-description">{{ step.description }}</p>
              </div>
            </div>
            <div class="step-action" v-if="step.action">
              <GradientButton @click="navigateTo(step.path)">
                {{ step.action }}
              </GradientButton>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
    
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import RecipeCard from '../components/RecipeCard.vue';
import RecipeMarquee from '../components/RecipeMarquee.vue';
import GlassCard3D from '../components/GlassCard3D.vue';
import GradientButton from '../components/GradientButton.vue';
import { getAllRecipesService as getAllRecipes } from '../api/recipeService';

const router = useRouter();
const { t } = useI18n();
const featuresSection = ref(null);
const loading = ref(false);
const trendingRecipes = ref([]);

// 功能特色配置
const featuresData = computed(() => [
  {
    title: t('home.features.aiNutritionAssistant.title'),
    description: t('home.features.aiNutritionAssistant.description'),
    emoji: '🤖',
    ctaText: t('home.features.aiNutritionAssistant.action'),
    path: '/ai-coach',
    delay: '0ms'
  },
  {
    title: t('home.features.aiRecommend.title'),
    description: t('home.features.aiRecommend.description'),
    emoji: '💬',
    ctaText: t('home.tryFeature'),
    path: '/ai-recommend',
    delay: '100ms'
  },
  {
    title: t('home.features.limitedConditions.title'),
    description: t('home.features.limitedConditions.description'),
    emoji: '🍳',
    ctaText: t('home.tryFeature'),
    path: '/limited-conditions',
    delay: '200ms'
  },
  {
    title: t('home.features.randomRecipe.title'),
    description: t('home.features.randomRecipe.description'),
    emoji: '🎲',
    ctaText: t('home.tryFeature'),
    path: '/random-recipe',
    delay: '300ms'
  },
  {
    title: t('home.features.gallery.title'),
    description: t('home.features.gallery.description'),
    emoji: '🍽️',
    ctaText: t('home.tryFeature'),
    path: '/food-gallery',
    delay: '400ms'
  },
  {
    title: t('home.features.myRecipes.title'),
    description: t('home.features.myRecipes.description'),
    emoji: '⭐',
    ctaText: t('home.tryFeature'),
    path: '/my-recipes',
    delay: '500ms'
  }
]);

// 暗色模式检测
const isDarkMode = computed(() => {
  if (typeof window !== 'undefined') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  return false;
});

// 如何使用步骤
const howItWorksSteps = computed(() => [
  {
    title: t('home.howItWorks.steps.step1.title'),
    description: t('home.howItWorks.steps.step1.description'),
    emoji: '👤',
    path: '/ai-recommend',
    action: t('home.howItWorks.steps.step1.action'),
  },
  {
    title: t('home.howItWorks.steps.step2.title'),
    description: t('home.howItWorks.steps.step2.description'),
    emoji: '🛒',
    path: '/limited-conditions',
    action: t('home.howItWorks.steps.step2.action'),
  },
  {
    title: t('home.howItWorks.steps.step3.title'),
    description: t('home.howItWorks.steps.step3.description'),
    emoji: '🎲',
    path: '/random-recipe',
    action: t('home.howItWorks.steps.step3.action'),
  },
  {
    title: t('home.howItWorks.steps.step4.title'),
    description: t('home.howItWorks.steps.step4.description'),
    emoji: '⭐',
    path: '/my-recipes',
    action: t('home.howItWorks.steps.step4.action'),
  },
]);

// 导航到指定路由
const navigateTo = (path) => {
  router.push(path);
};

// 滚动到功能区域
const scrollToFeatures = () => {
  featuresSection.value.scrollIntoView({ behavior: 'smooth' });
};

// 收藏状态改变
const onFavoriteChange = ({ recipe, isFavorite }) => {
  const actionText = isFavorite ? t('home.notifications.addedToFavorites') : t('home.notifications.removedFromFavorites');
  ElMessage.success(`${t('home.notifications.successfully')} ${actionText} 「${recipe.name}」`);
};

// 处理菜谱点击
const onRecipeClick = (recipe) => {
  console.log('Recipe clicked:', recipe);
  // 可以在这里添加额外的点击处理逻辑，如统计等
};

// 加载随机菜谱
const loadRandomRecipes = async () => {
  loading.value = true;
  try {
    const allRecipes = await getAllRecipes();
    
    // 随机打乱并获取前8个
    const shuffled = allRecipes.sort(() => 0.5 - Math.random());
    trendingRecipes.value = shuffled.slice(0, 8);
    
  } catch (error) {
    console.error(t('home.errors.loadTrendingFailed'), error);
    trendingRecipes.value = [];
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadRandomRecipes();
});
</script>

<style scoped>

/* 旋转边框动画 */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.home-page {
  min-height: 100vh;
  background: transparent !important;
  position: relative;
  overflow-x: hidden;
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 背景层 */
.hero-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -1;
}

/* 径向渐变背景 */
.radial-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(
      ellipse 20% 80% at 50% -20%,
      rgba(75, 85, 150, 0.4),
      transparent
    ),
    linear-gradient(
      135deg,
      rgba(88, 28, 135, 0.15) 0%,
      rgba(139, 69, 19, 0.1) 50%,
      rgba(30, 58, 138, 0.15) 100%
    );
  transition: background 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 亮色模式的径向渐变 */
:root:not(.dark) .home-page {
  background: transparent !important;
}

:root:not(.dark) .radial-gradient {
  background: 
    radial-gradient(
      ellipse 20% 80% at 50% -20%,
      rgba(120, 119, 198, 0.15),
      transparent
    ),
    linear-gradient(
      135deg,
      rgba(168, 85, 247, 0.05) 0%,
      rgba(236, 72, 153, 0.05) 50%,
      rgba(59, 130, 246, 0.05) 100%
    );
}

/* 紫色光晕层 */
.purple-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(
      ellipse 40% 60% at 30% 20%, 
      rgba(88, 28, 135, 0.2), 
      transparent 50%
    ),
    radial-gradient(
      ellipse 50% 80% at 70% 80%, 
      rgba(67, 56, 202, 0.15), 
      transparent 50%
    ),
    radial-gradient(
      ellipse 60% 40% at 50% 50%, 
      rgba(139, 69, 19, 0.1), 
      transparent 50%
    );
  filter: blur(3px);
  opacity: 0.9;
  transition: background 0.8s cubic-bezier(0.4, 0, 0.2, 1), 
              opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 亮色模式的紫色光晕 */
:root:not(.dark) .purple-glow {
  background: 
    radial-gradient(
      ellipse 40% 60% at 30% 20%, 
      rgba(168, 85, 247, 0.08), 
      transparent 50%
    ),
    radial-gradient(
      ellipse 50% 80% at 70% 80%, 
      rgba(147, 51, 234, 0.06), 
      transparent 50%
    ),
    radial-gradient(
      ellipse 60% 40% at 50% 50%, 
      rgba(236, 72, 153, 0.04), 
      transparent 50%
    );
  opacity: 0.6;
}

/* Hero 区域 */
.hero-section {
  position: relative;
  z-index: 10;
  padding: 7rem 1rem;
  text-align: center;
  max-width: 1280px;
  margin: 0 auto;
  background: transparent;
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.hero-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3rem;
  background: transparent;
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}



/* 主标题 */
.hero-title {
  font-family: 'Geist', system-ui, sans-serif;
  font-size: clamp(2.5rem, 8vw, 4rem);
  font-weight: 700;
  letter-spacing: -0.05em;
  margin: 0;
  line-height: 1.1;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.title-main {
  display: block;
  background: linear-gradient(
    135deg,
    #a855f7 0%,
    #ec4899 50%,
    #f97316 100%
  );
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: 0 0 30px rgba(168, 85, 247, 0.3);
}

/* 亮色模式的主标题 */
:root:not(.dark) .title-main {
  background: linear-gradient(
    135deg,
    #7c3aed 0%,
    #db2777 50%,
    #ea580c 100%
  );
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: 0 0 30px rgba(124, 58, 237, 0.2);
}

/* 副标题 */
.hero-subtitle {
  font-size: 1rem;
  max-width: 32rem;
  color: #ffffff;
  margin: 0;
  line-height: 1.6;
}

/* 亮色模式的副标题 */
:root:not(.dark) .hero-subtitle {
  color: #6b7280;
}

/* CTA 按钮区域 */
.hero-actions {
  margin-top: 1rem;
}

/* CTA 按钮容器 */
.cta-wrapper {
  position: relative;
  display: inline-block;
  overflow: hidden;
  border-radius: 50px;
  padding: 1.5px;
}

/* 旋转边框动画 */
.cta-border-animation {
  position: absolute;
  inset: -1000%;
  width: 2000%;
  height: 2000%;
  background: conic-gradient(
    from 90deg at 50% 50%,
    #E2CBFF 0%,
    #393BB2 50%,
    #E2CBFF 100%
  );
  animation: spin 2s linear infinite;
  z-index: 0;
}

/* CTA 按钮 */
.cta-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 1rem 2.5rem;
  border-radius: 50px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.05) 0%,
    rgba(168, 85, 247, 0.1) 50%,
    transparent 100%
  );
  color: #ffffff !important;
  font-weight: 600;
  font-size: 1rem;
  text-decoration: none;
  cursor: pointer;
  backdrop-filter: blur(20px);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  z-index: 1;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.cta-button:hover {
  transform: translateY(-2px) scale(1.02);
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.1) 0%,
    rgba(168, 85, 247, 0.2) 50%,
    transparent 100%
  );
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 
    0 16px 40px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
  color: #ffffff !important;
}

/* 亮色模式边框动画 */
:root:not(.dark) .cta-border-animation {
  background: conic-gradient(
    from 90deg at 50% 50%,
    #C2A5F5 0%,
    #6366F1 50%,
    #C2A5F5 100%
  );
}

/* 亮色模式 CTA 按钮 */
:root:not(.dark) .cta-button {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.8) 0%,
    rgba(139, 92, 246, 0.1) 50%,
    transparent 100%
  );
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #1e293b !important;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

:root:not(.dark) .cta-button:hover {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.9) 0%,
    rgba(139, 92, 246, 0.2) 50%,
    transparent 100%
  );
  border-color: rgba(0, 0, 0, 0.2);
  color: #0f172a !important;
  box-shadow: 
    0 16px 40px rgba(0, 0, 0, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 1);
}

/* 按钮按下效果 */
.cta-button:active {
  transform: translateY(-1px) scale(0.99);
  transition: transform 0.1s ease;
}

.cta-wrapper:hover .cta-border-animation {
  animation-duration: 1s;
}

/* 内容区域样式 */
.section-title {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 15px;
  color: #ffffff;
}

.section-description {
  text-align: center;
  max-width: 700px;
  margin: 0 auto 40px;
  color: #d1d5db;
  font-size: 1.1rem;
}

.features-section {
  padding: 20px;
  margin-bottom: 60px;
  position: relative;
  z-index: 10;
  background: transparent !important;
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 玻璃卡片网格布局 */
.glass-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
  gap: 30px;
  justify-items: center;
  padding: 20px 0;
  margin-bottom: 30px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .glass-cards-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 25px;
  }
}

@media (max-width: 768px) {
  .glass-cards-grid {
    grid-template-columns: 1fr;
    gap: 20px;
    padding: 10px 0;
  }
  
  .features-section {
    padding: 15px;
  }
}

@media (max-width: 480px) {
  .glass-cards-grid {
    padding: 0;
  }
}

.how-it-works-section {
  padding: 20px;
  margin-bottom: 60px;
  background: linear-gradient(
    135deg,
    rgba(25, 25, 30, 0.85),
    rgba(60, 25, 80, 0.7)
  );
  border: 1px solid rgba(147, 51, 234, 0.25);
  border-radius: 12px;
  backdrop-filter: blur(16px);
  position: relative;
  z-index: 10;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.timeline-card {
  margin-left: 10px;
  background: linear-gradient(
    135deg,
    rgba(35, 35, 40, 0.7),
    rgba(70, 35, 110, 0.5)
  );
  border: 1px solid rgba(147, 51, 234, 0.2);
  backdrop-filter: blur(16px);
  box-shadow: 
    0 4px 16px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.step-content {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.step-icon {
  font-size: 2rem;
  color: #a855f7;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: linear-gradient(
    135deg,
    rgba(168, 85, 247, 0.3),
    rgba(168, 85, 247, 0.15)
  );
  border: 2px solid rgba(168, 85, 247, 0.4);
  box-shadow: 
    0 4px 12px rgba(168, 85, 247, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.step-text {
  flex: 1;
}

.step-title {
  margin: 0 0 5px;
  font-size: 1.1rem;
  color: #ffffff;
  font-weight: 600;
}

.step-description {
  margin: 0;
  color: #f3f4f6;
  font-size: 0.95rem;
  line-height: 1.4;
}

.step-action {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}



/* 亮色模式适配 */
:root:not(.dark) .section-title {
  color: #111827;
}

:root:not(.dark) .section-description {
  color: #6b7280;
}



:root:not(.dark) .how-it-works-section {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.98),
    rgba(248, 250, 252, 1)
  );
  border: 2px solid rgba(139, 92, 246, 0.25);
  box-shadow: 
    0 12px 40px rgba(0, 0, 0, 0.15),
    0 3px 12px rgba(139, 92, 246, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

:root:not(.dark) .timeline-card {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.95),
    rgba(248, 250, 252, 0.98)
  );
  border: 1.5px solid rgba(168, 85, 247, 0.2);
  box-shadow: 
    0 6px 24px rgba(0, 0, 0, 0.12),
    0 2px 8px rgba(168, 85, 247, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

:root:not(.dark) .step-icon {
  color: #7c3aed;
  background: linear-gradient(
    135deg,
    rgba(124, 58, 237, 0.2),
    rgba(124, 58, 237, 0.12)
  );
  border: 2px solid rgba(124, 58, 237, 0.4);
  box-shadow: 
    0 6px 16px rgba(124, 58, 237, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

:root:not(.dark) .step-title {
  color: #111827;
}

:root:not(.dark) .step-description {
  color: #6b7280;
}



/* 确保按钮和链接文字为白色 */
.feature-card .el-button--text {
  color: #ffffff !important;
}

.feature-card .el-button--text:hover {
  color: #f3f4f6 !important;
}

:root:not(.dark) .feature-card .el-button--text {
  color: #1f2937 !important;
  font-weight: 600;
}

:root:not(.dark) .feature-card .el-button--text:hover {
  color: #111827 !important;
}

/* GradientButton在step-action中的样式调整 */
.step-action .gradient-button {
  min-width: 120px;
  padding: 0.75rem 1.75rem;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .section-title {
    font-size: 1.8rem;
  }
  
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .hero-actions .el-button {
    width: 80%;
  }
  
  .step-content {
    flex-direction: column;
    text-align: center;
  }
  
  .step-action {
    justify-content: center;
  }
  
  .step-action .gradient-button {
    min-width: 100px;
    padding: 0.625rem 1.5rem;
    font-size: 0.85rem;
  }
}
</style>
