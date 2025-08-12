<template>
  <div class="food-gallery-container">
    <!-- Sparkles 粒子动画背景 -->
    <div class="sparkles-container">
      <div 
        v-for="sparkle in sparkles" 
        :key="sparkle.id"
        :class="['sparkle', sparkle.size, sparkle.intensity]"
        :style="{
          left: sparkle.x + '%',
          top: sparkle.y + '%',
          animationDelay: sparkle.delay + 's',
          animationDuration: sparkle.duration + 's',
          '--move-x': sparkle.moveX + 'px',
          '--move-y': sparkle.moveY + 'px'
        }"
      >
        <div class="sparkle-inner"></div>
      </div>
    </div>
    
    <!-- 页面标题 -->
    <div class="header fade-in-section" data-aos="fade-up" data-aos-duration="800">
      <h1 class="title animated-title">{{ t('foodGallery.title') }}</h1>
      <div class="title-accent" aria-hidden="true"></div>
      <p class="description">{{ t('foodGallery.description') }}</p>
    </div>

    <!-- AI智能搜索区域 -->
    <el-card class="ai-search-card fade-in-section" data-aos="fade-up" data-aos-duration="1000" data-aos-delay="200">
      <div class="ai-search-area">
        <h3 class="ai-search-title">{{ t('foodGallery.aiSearchTitle') }}</h3>
        <p class="ai-search-description">{{ t('foodGallery.aiSearchDescription') }}</p>
        
        <!-- API状态警告 -->
        <el-alert
          v-if="!isSearchApiAvailable"
          type="warning"
          :closable="false"
          show-icon
          :title="t('foodGallery.apiUnavailable')"
          class="api-alert"
        >
          <template #default>
            {{ t('foodGallery.apiUnavailableDesc') }}
          </template>
        </el-alert>
        
                 <!-- 搜索输入框 -->
         <div class="search-input-wrapper" data-aos="zoom-in" data-aos-duration="800" data-aos-delay="400">
           <el-input 
             v-model="aiSearchQuery" 
             :placeholder="t('foodGallery.aiSearchPlaceholder')" 
             @keyup.enter="handleAiSearch"
             size="large"
             class="ai-search-input modern-input"
           >
                         <template #append>
              <GradientButton 
                :loading="isAiSearching" 
                @click="handleAiSearch" 
                variant="default"
                class="gradient-search-button"
              >
                {{ t('common.search') }}
              </GradientButton>
            </template>
           </el-input>
         </div>
         
         <!-- 清除搜索按钮 -->
         <div v-if="aiSearchQuery.trim() || searchResults" class="search-actions" style="margin-top: 16px;">
           <el-button 
             type="warning" 
             size="default" 
             @click="clearSearch" 
             plain 
             class="clear-search-btn"
             style="border-radius: 20px; font-weight: 600;"
           >
             🗑️ {{ t('common.clearSearch') }}
           </el-button>
         </div>
        
        <!-- 搜索结果信息 -->
        <div v-if="searchResults && searchMessage" class="search-result-info fade-in-section" data-aos="slide-up" data-aos-duration="500">
          <p>{{ searchMessage }}</p>
        </div>
        
        <!-- 推荐查询 -->
        <div v-if="suggestedQueries && suggestedQueries.length > 0" class="suggested-queries fade-in-section" data-aos="fade-up" data-aos-duration="600" data-aos-delay="100">
          <span>{{ t('foodGallery.suggestedQueries') }}: </span>
          <el-tag 
            v-for="(query, index) in suggestedQueries" 
            :key="query" 
            size="small" 
            @click="useSuggestedQuery(query)"
            effect="light"
            class="clickable-tag modern-tag"
            :data-aos-delay="(index * 100) + 200"
            data-aos="zoom-in"
            data-aos-duration="400"
          >
            {{ query }}
          </el-tag>
        </div>
      </div>
    </el-card>

    <!-- 搜索分析结果 -->
    <el-collapse v-if="searchAnalysis && searchResults && searchResults.length > 0" class="search-analysis fade-in-section" data-aos="fade-up" data-aos-duration="800" data-aos-delay="300">
      <el-collapse-item>
        <template #title>
          <span class="analysis-title">{{ t('foodGallery.searchAnalysis') }}</span>
        </template>
        
        <div class="analysis-content">
          <div v-if="searchAnalysis.intent" class="analysis-item">
            <span class="analysis-label">{{ t('foodGallery.searchIntent') }}:</span>
            <span class="analysis-value">{{ searchAnalysis.intent }}</span>
          </div>
          
          <div v-if="searchAnalysis.extractedFeatures" class="analysis-item">
            <div v-if="searchAnalysis.extractedFeatures.cuisine && searchAnalysis.extractedFeatures.cuisine.length > 0">
              <span class="analysis-label">{{ t('foodGallery.detectedCuisine') }}:</span>
              <el-tag v-for="cuisine in searchAnalysis.extractedFeatures.cuisine" :key="cuisine" size="small">
                {{ cuisine }}
              </el-tag>
            </div>
            
            <div v-if="searchAnalysis.extractedFeatures.cooking_method && searchAnalysis.extractedFeatures.cooking_method.length > 0">
              <span class="analysis-label">{{ t('foodGallery.detectedMethod') }}:</span>
              <el-tag v-for="method in searchAnalysis.extractedFeatures.cooking_method" :key="method" size="small">
                {{ method }}
              </el-tag>
            </div>
            
            <div v-if="searchAnalysis.extractedFeatures.taste && searchAnalysis.extractedFeatures.taste.length > 0">
              <span class="analysis-label">{{ t('foodGallery.detectedTaste') }}:</span>
              <el-tag v-for="taste in searchAnalysis.extractedFeatures.taste" :key="taste" size="small">
                {{ taste }}
              </el-tag>
            </div>
            
            <div v-if="searchAnalysis.extractedFeatures.ingredients && searchAnalysis.extractedFeatures.ingredients.length > 0">
              <span class="analysis-label">{{ t('foodGallery.detectedIngredients') }}:</span>
              <el-tag v-for="ingredient in searchAnalysis.extractedFeatures.ingredients" :key="ingredient" size="small" type="success">
                {{ ingredient }}
              </el-tag>
            </div>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>

    <!-- 食谱网格展示 -->
    <div v-loading="isLoading || isAiSearching" class="recipe-grid-wrapper fade-in-section" data-aos="fade-up" data-aos-duration="1000" data-aos-delay="400">
      <el-row v-if="paginatedRecipes.length > 0" :gutter="20" class="recipe-grid">
        <el-col 
          v-for="(recipe, index) in paginatedRecipes" 
          :key="recipe.id" 
          :xs="24" 
          :sm="12" 
          :md="8" 
          :lg="6"
          class="recipe-col"
          :data-aos-delay="(index % 8) * 100 + 600"
          data-aos="zoom-in"
          data-aos-duration="600"
        >
          <RecipeCard :recipe="recipe" />
        </el-col>
      </el-row>
      <el-empty 
        v-if="!isLoading && !isAiSearching && paginatedRecipes.length === 0" 
        :description="searchResults ? t('foodGallery.noSearchResults') : t('foodGallery.noResults')"
        class="modern-empty"
        data-aos="fade-in"
        data-aos-duration="800"
      />
    </div>

    <!-- 分页组件 -->
    <div v-if="displayedRecipes.length > pageSize" class="pagination-wrapper">
      <el-pagination
        background
        layout="prev, pager, next"
        :total="displayedRecipes.length"
        :page-size="pageSize"
        v-model:current-page="currentPage"
        class="modern-pagination"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import RecipeCard from '../components/RecipeCard.vue';
import GradientButton from '../components/GradientButton.vue';
import { getAllRecipesService as getRecipes } from '../api/recipeService';
import { searchRecipes, getSearchSuggestions, checkApiHealth as checkSearchApiHealth } from '../api/aiRecipeSearchService';
import { directSearchRecipes, directHealthCheck, diagnosiseSearchFunction } from '../api/fixedRecipeSearchService';

const { t } = useI18n();

// 数据状态
const allRecipes = ref([]);
const isLoading = ref(true);
const currentPage = ref(1);
const pageSize = 12;

// Sparkles 粒子动画状态
const sparkles = ref([]);
const sparkleId = ref(0);

// 搜索相关状态
const aiSearchQuery = ref('');
const isAiSearching = ref(false);
const searchResults = ref(null);
const searchAnalysis = ref(null);
const suggestedQueries = ref([]);
const searchMessage = ref('');
const isSearchApiAvailable = ref(true);

// 计算属性
const displayedRecipes = computed(() => {
  // 如果有搜索结果，显示搜索结果；否则显示所有食谱
  if (searchResults.value) {
    return searchResults.value;
  }
  
  // 按热度排序显示所有食谱
  return [...allRecipes.value].sort((a, b) => (b.popularity || 0) - (a.popularity || 0));
});

const paginatedRecipes = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  const end = start + pageSize;
  return displayedRecipes.value.slice(start, end);
});

// 检查后端API可用性 - 使用修复版服务
async function checkBackendAvailability() {
  try {
    console.log('🏥 检查后端可用性...');
    const searchAvailable = await directHealthCheck();
    isSearchApiAvailable.value = searchAvailable.isHealthy;
    
    if (searchAvailable.isHealthy) {
      console.log('✅ 后端服务正常:', searchAvailable.message);
    } else {
      console.warn('⚠️ 后端服务不可用:', searchAvailable.message);
    }
  } catch (error) {
    console.error('❌ 检查搜索API状态失败:', error);
    isSearchApiAvailable.value = false;
  }
}

// AI搜索处理函数 - 使用修复版服务
const handleAiSearch = async () => {
  if (!aiSearchQuery.value.trim()) return;
  
  isAiSearching.value = true;
  currentPage.value = 1; // 重置分页
  ElMessage.info(t('foodGallery.aiSearching'));
  
  try {
    console.log('🔍 开始搜索，关键词:', aiSearchQuery.value);
    
    // 使用修复版搜索API
    const result = await directSearchRecipes(aiSearchQuery.value, 600);
    
    console.log('📊 搜索结果:', result);
    
    if (!result.success || result.error) {
      console.error('❌ 搜索失败:', result.error);
      ElMessage.warning(`${t('foodGallery.searchError')}: ${result.message || result.error}`);
      searchMessage.value = result.message || t('foodGallery.searchErrorTryAgain');
      searchResults.value = [];
    } else if (result.recipes.length === 0) {
      console.log('ℹ️ 无搜索结果');
      ElMessage.info(t('foodGallery.noResults'));
      searchMessage.value = t('foodGallery.tryDifferentQuery');
      searchResults.value = [];
    } else {
      console.log('✅ 搜索成功，找到', result.recipes.length, '个结果');
      ElMessage.success(`${t('foodGallery.aiSearchSuccess')} (${result.totalResults})`);
      searchMessage.value = result.message || `找到${result.recipes.length}个相关菜谱`;
      searchResults.value = result.recipes;
      
      // 生成搜索建议
      try {
        const suggestions = await getSearchSuggestions(aiSearchQuery.value, result.recipes);
        if (suggestions && suggestions.suggestedQueries) {
          suggestedQueries.value = suggestions.suggestedQueries;
        }
      } catch (suggestionsError) {
        console.error('生成搜索建议失败:', suggestionsError);
      }
    }
    
    // 更新搜索分析
    searchAnalysis.value = result.analysis || null;
    
  } catch (error) {
    console.error('❌ 搜索过程出错:', error);
    ElMessage.error(`${t('foodGallery.searchError')}: ${error.message}`);
    searchResults.value = [];
    searchMessage.value = t('foodGallery.searchErrorTryAgain');
  } finally {
    isAiSearching.value = false;
  }
};

// 清除搜索
const clearSearch = () => {
  searchResults.value = null;
  searchAnalysis.value = null;
  suggestedQueries.value = [];
  searchMessage.value = '';
  aiSearchQuery.value = '';
  currentPage.value = 1;
};

// 使用建议查询
const useSuggestedQuery = (query) => {
  aiSearchQuery.value = query;
  handleAiSearch();
};

// 创建单个sparkle粒子
const createSparkle = () => {
  const sizes = ['small', 'medium', 'large'];
  const intensities = ['dim', 'normal', 'bright'];
  
  return {
    id: sparkleId.value++,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: sizes[Math.floor(Math.random() * sizes.length)],
    intensity: intensities[Math.floor(Math.random() * intensities.length)],
    delay: Math.random() * 4,
    duration: 1.5 + Math.random() * 3.5,
    moveX: (Math.random() - 0.5) * 2, // -1 到 1 的随机值
    moveY: (Math.random() - 0.5) * 2
  };
};

// 初始化sparkles
const initSparkles = () => {
  sparkles.value = [];
  // 创建初始粒子
  for (let i = 0; i < 20; i++) {
    sparkles.value.push(createSparkle());
  }
  
  // 定期添加新粒子
  sparkleInterval = setInterval(() => {
    if (sparkles.value.length < 30) {
      sparkles.value.push(createSparkle());
    }
    
    // 移除过期粒子
    sparkles.value = sparkles.value.filter((sparkle, index) => {
      return index < 25; // 保持最多25个粒子
    });
  }, 800);
};

// 滚动观察器
let intersectionObserver = null;

// 初始化滚动动画
const initScrollAnimations = () => {
  intersectionObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          // 为食谱卡片添加延迟动画
          if (entry.target.classList.contains('recipe-col')) {
            const index = parseInt(entry.target.dataset.index || '0');
            entry.target.style.animationDelay = `${index * 100}ms`;
          }
        }
      });
    },
    {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    }
  );

  // 观察所有需要动画的元素
  setTimeout(() => {
    const animatedElements = document.querySelectorAll('.fade-in-section, [data-aos]');
    animatedElements.forEach((el) => {
      intersectionObserver.observe(el);
    });
  }, 100);
};

// 粒子动画定时器
let sparkleInterval = null;

// 组件挂载时初始化
onMounted(async () => {
  console.log('🎯 美食展厅开始初始化...');
  isLoading.value = true;
  
  // 初始化sparkles动画
  initSparkles();
  
  // 异步执行后台检查（不阻塞主流程）
  Promise.all([
    checkBackendAvailability(),
    // 开发环境的诊断检查也放到后台异步执行
    import.meta.env.DEV ? runDevDiagnostics() : Promise.resolve()
  ]).catch(error => {
    console.warn('⚠️ 后台检查过程中出现错误:', error);
  });
  
  // 优先加载食谱数据
  try {
    console.log('📖 开始加载菜谱数据...');
    const startTime = Date.now();
    const data = await getRecipes();
    const loadTime = Date.now() - startTime;
    console.log(`📊 获取到的数据: ${data?.length || 0} 个菜谱，耗时: ${loadTime}ms`);
    
    if (Array.isArray(data) && data.length > 0) {
      allRecipes.value = data;
      console.log(`✅ 成功加载 ${data.length} 个菜谱`);
      // 只在首次加载时显示成功消息
      if (loadTime > 100) {
        ElMessage.success(`成功加载 ${data.length} 个菜谱`);
      }
    } else {
      console.warn('⚠️ 菜谱数据为空或格式错误');
      allRecipes.value = [];
      ElMessage.warning('未找到菜谱数据，请检查数据文件');
    }
  } catch (error) {
    console.error('❌ 加载菜谱数据失败:', error);
    allRecipes.value = [];
    ElMessage.error(`加载菜谱失败: ${error.message}`);
  } finally {
    isLoading.value = false;
    console.log('🎯 美食展厅初始化完成，当前菜谱数量:', allRecipes.value.length);
    // 初始化滚动动画
    initScrollAnimations();
  }
});

// 开发环境诊断函数
async function runDevDiagnostics() {
  if (!import.meta.env.DEV) return;
  
  try {
    console.log('🔬 开发环境：运行搜索功能诊断...');
    const diagnosis = await diagnosiseSearchFunction();
    console.log('📊 搜索功能诊断报告:', diagnosis);
    
    if (!diagnosis.summary.searchWorking) {
      console.warn('⚠️ 搜索功能存在问题，请检查后端服务');
    } else {
      console.log('✅ 搜索功能正常工作');
    }
  } catch (diagnosisError) {
    console.error('❌ 搜索诊断失败:', diagnosisError);
  }
}

// 组件卸载时清理
onUnmounted(() => {
  if (intersectionObserver) {
    intersectionObserver.disconnect();
  }
  
  if (sparkleInterval) {
    clearInterval(sparkleInterval);
  }
});
</script>

<style scoped>
.food-gallery-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  overflow-x: hidden;
  /* 确保不产生垂直滚动条 */
  overflow-y: visible;
  /* 确保容器高度自适应内容 */
  min-height: auto;
  height: auto;
  /* 防止滚动条导致的布局跳动 */
  width: 100%;
  box-sizing: border-box;
  /* 确保内容区域宽度稳定，考虑滚动条空间 */
  padding-right: calc(24px + env(scrollbar-width, 0px));
  padding-left: 24px;
}

/* Sparkles 粒子动画背景 */
.sparkles-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  pointer-events: none;
  overflow: hidden;
}

.sparkle {
  position: absolute;
  pointer-events: none;
  animation: sparkleAnimation infinite ease-in-out;
  will-change: transform, opacity;
  backface-visibility: hidden;
  transform-style: preserve-3d;
}

.sparkle-inner {
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.8) 0%, transparent 70%);
  border-radius: 50%;
  animation: sparkleGlow infinite ease-in-out alternate;
  will-change: box-shadow, background;
  backface-visibility: hidden;
}

/* 不同尺寸的sparkle */
.sparkle.small {
  width: 4px;
  height: 4px;
}

.sparkle.medium {
  width: 8px;
  height: 8px;
}

.sparkle.large {
  width: 12px;
  height: 12px;
}

/* 不同亮度的sparkle */
.sparkle.dim .sparkle-inner {
  opacity: 0.6;
  filter: brightness(0.7);
}

.sparkle.normal .sparkle-inner {
  opacity: 0.8;
  filter: brightness(1);
}

.sparkle.bright .sparkle-inner {
  opacity: 1;
  filter: brightness(1.3);
}

/* Sparkle 动画 */
@keyframes sparkleAnimation {
  0% {
    opacity: 0;
    transform: scale(0) rotate(0deg) translate(0, 0);
  }
  10% {
    opacity: 0.3;
    transform: scale(0.3) rotate(45deg) translate(calc(var(--move-x) * 0.2), calc(var(--move-y) * 0.2));
  }
  20% {
    opacity: 1;
    transform: scale(1) rotate(90deg) translate(calc(var(--move-x) * 0.5), calc(var(--move-y) * 0.5));
  }
  50% {
    opacity: 1;
    transform: scale(1.1) rotate(180deg) translate(calc(var(--move-x) * 1), calc(var(--move-y) * 1));
  }
  80% {
    opacity: 1;
    transform: scale(0.8) rotate(270deg) translate(calc(var(--move-x) * 0.7), calc(var(--move-y) * 0.7));
  }
  90% {
    opacity: 0.5;
    transform: scale(0.3) rotate(315deg) translate(calc(var(--move-x) * 0.3), calc(var(--move-y) * 0.3));
  }
  100% {
    opacity: 0;
    transform: scale(0) rotate(360deg) translate(0, 0);
  }
}

@keyframes sparkleGlow {
  0% {
    box-shadow: 0 0 6px rgba(102, 126, 234, 0.6), 0 0 12px rgba(118, 75, 162, 0.4);
    background: radial-gradient(circle, rgba(102, 126, 234, 0.8) 0%, transparent 70%);
  }
  25% {
    box-shadow: 0 0 8px rgba(240, 147, 251, 0.7), 0 0 16px rgba(245, 87, 108, 0.5);
    background: radial-gradient(circle, rgba(240, 147, 251, 0.8) 0%, transparent 70%);
  }
  50% {
    box-shadow: 0 0 10px rgba(245, 87, 108, 0.8), 0 0 20px rgba(102, 126, 234, 0.6);
    background: radial-gradient(circle, rgba(245, 87, 108, 0.8) 0%, transparent 70%);
  }
  75% {
    box-shadow: 0 0 8px rgba(118, 75, 162, 0.7), 0 0 16px rgba(240, 147, 251, 0.5);
    background: radial-gradient(circle, rgba(118, 75, 162, 0.8) 0%, transparent 70%);
  }
  100% {
    box-shadow: 0 0 6px rgba(102, 126, 234, 0.6), 0 0 12px rgba(118, 75, 162, 0.4);
    background: radial-gradient(circle, rgba(102, 126, 234, 0.8) 0%, transparent 70%);
  }
}

.header {
  margin-bottom: 32px;
  text-align: center;
}

.title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--el-text-color-primary);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
}

.animated-title { position: relative; }

/* 取消原有的标题光波动画，改为下方渐变发光分隔线与轻微呼吸效果 */
.title-accent {
  height: 10px;
  width: clamp(160px, 40vw, 420px);
  margin: 10px auto 6px;
  border-radius: 999px;
  background: radial-gradient(60% 60% at 50% 50%, rgba(118,75,162,.35), rgba(102,126,234,.2), transparent 70%);
  filter: blur(6px);
  position: relative;
}

.title-accent::before {
  content: '';
  position: absolute;
  inset: -6px -20px;
  border-radius: 999px;
  background: conic-gradient(from 0deg, rgba(118,75,162,.15), rgba(102,126,234,.15), rgba(240,147,251,.15), rgba(118,75,162,.15));
  animation: rotateGlow 10s linear infinite;
  filter: blur(14px);
  opacity: .9;
}

@keyframes rotateGlow {
  to { transform: rotate(360deg); }
}

.description {
  font-size: 1.1rem;
  color: var(--el-text-color-secondary);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.ai-search-card {
  margin-bottom: 32px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 8px 16px rgba(0, 0, 0, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  border-radius: 24px;
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  /* 确保卡片内容不产生滚动条 */
  height: auto;
  max-height: none;
}

/* 重写Element Plus卡片组件的默认样式 */
.ai-search-card :deep(.el-card__body) {
  padding: 0 !important;
  overflow: visible !important;
  height: auto !important;
  max-height: none !important;
}

.ai-search-card:hover {
  transform: translateY(-4px);
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.15),
    0 12px 24px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.ai-search-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
}

.ai-search-area {
  padding: 24px;
  /* 确保搜索区域不产生滚动条 */
  overflow: visible;
  height: auto;
  max-height: none;
}

.ai-search-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--el-text-color-primary);
}

.ai-search-description {
  margin-bottom: 24px;
  font-size: 1rem;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}

/* 搜索输入框包装器 */
.search-input-wrapper {
  max-width: 700px;
  margin: 0 auto 20px;
}

.ai-search-input {
  width: 100%;
}

.modern-input :deep(.el-input__wrapper) {
  border-radius: 20px;
  box-shadow: 
    0 8px 24px rgba(0, 0, 0, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 60px;
}

/* 修复输入框文字颜色和光标 */
.modern-input :deep(.el-input__inner) {
  color: #2c3e50 !important;
  font-size: 16px;
  font-weight: 500;
  caret-color: #667eea !important; /* 光标颜色 */
}

.modern-input :deep(.el-input__inner)::placeholder {
  color: #8492a6 !important;
  font-weight: 400;
}

.modern-input :deep(.el-input__wrapper):hover {
  box-shadow: 
    0 12px 32px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
  transform: translateY(-2px);
}

.modern-input :deep(.el-input__wrapper):focus-within {
  box-shadow: 
    0 0 0 3px rgba(102, 126, 234, 0.2),
    0 12px 32px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
  border-color: rgba(102, 126, 234, 0.5);
}

.modern-input :deep(.el-input__inner) {
  font-size: 1.1rem;
  padding: 18px 24px;
  font-weight: 500;
  letter-spacing: 0.3px;
}

/* 渐变搜索按钮样式 */
.gradient-search-button {
  border-radius: 0 20px 20px 0 !important;
  min-width: 120px !important;
  min-height: 60px !important;
  border: none !important;
  margin: 0 !important;
}

/* Element Plus 输入框附加区域样式适配 */
.ai-search-input :deep(.el-input-group__append) {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  border-radius: 0 20px 20px 0 !important;
  overflow: hidden;
}

.ai-search-input :deep(.el-input-group__append .gradient-button) {
  border-radius: 0 18px 18px 0 !important;
  min-height: 58px !important;
}

/* 现代按钮样式（用于其他按钮） */
.modern-button {
  border-radius: 18px !important;
  font-weight: 600 !important;
  letter-spacing: 0.5px !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
  border: none !important;
  position: relative !important;
  overflow: hidden !important;
}

.modern-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  transition: left 0.5s;
}

.modern-button:hover::before {
  left: 100%;
}

.clear-button {
  background: linear-gradient(135deg, rgba(118, 75, 162, 0.1), rgba(102, 126, 234, 0.1)) !important;
  color: var(--el-text-color-primary) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
}

.clear-button:hover {
  transform: translateY(-2px) !important;
  background: linear-gradient(135deg, rgba(118, 75, 162, 0.2), rgba(102, 126, 234, 0.2)) !important;
}

.search-actions {
  margin-bottom: 16px;
  text-align: center;
}

.search-result-info {
  margin-bottom: 20px;
  font-size: 15px;
  color: var(--el-text-color-secondary);
  padding: 16px 24px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08), rgba(118, 75, 162, 0.08));
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(8px);
  text-align: center;
  font-weight: 500;
}

.suggested-queries {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 15px;
  color: var(--el-text-color-secondary);
  padding: 16px 0;
}

.modern-tag {
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 20px !important;
  padding: 8px 16px !important;
  font-weight: 500 !important;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}

.modern-tag:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3) !important;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
}

.api-alert {
  margin-bottom: 16px;
  border-radius: 8px;
}

.search-analysis {
  margin-bottom: 24px;
}

.analysis-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.analysis-content {
  padding: 16px;
  font-size: 14px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
}

.analysis-item {
  margin-bottom: 12px;
}

.analysis-item:last-child {
  margin-bottom: 0;
}

.analysis-label {
  font-weight: 500;
  margin-right: 8px;
  color: var(--el-text-color-primary);
}

.analysis-value {
  color: var(--el-text-color-regular);
}

.el-tag {
  margin-right: 6px;
  margin-bottom: 6px;
}

/* 食谱网格样式 */
.recipe-grid-wrapper {
  margin-bottom: 40px;
  position: relative;
  /* 移除固定的最小高度，让内容自然展开 */
  min-height: auto;
  /* 确保不产生滚动条 */
  overflow: visible;
}

.recipe-grid {
  position: relative;
}

.recipe-col {
  margin-bottom: 24px;
}

.recipe-col:hover {
  z-index: 10;
}

.modern-empty {
  padding: 60px 40px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
}

/* 分页组件样式 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 40px;
  margin-bottom: 60px; /* 增加底部边距，确保有足够空间 */
  /* 确保分页组件立即可见且布局稳定 */
  opacity: 1;
  visibility: visible;
  /* 预留空间避免布局跳动 */
  min-height: 48px;
  /* 确保在所有浏览器中都能正确显示 */
  width: 100%;
  position: relative;
  z-index: 1;
  /* 确保内容始终可见 */
  flex-shrink: 0;
}

.modern-pagination :deep(.el-pagination) {
  gap: 8px;
}

.modern-pagination :deep(.el-pager li) {
  border-radius: 12px;
  margin: 0 4px;
  min-width: 40px;
  height: 40px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #2c3e50 !important; /* 修复数字颜色 */
  font-weight: 600;
}

.modern-pagination :deep(.el-pager li:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
}

.modern-pagination :deep(.el-pager li.is-active) {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.modern-pagination :deep(.btn-prev),
.modern-pagination :deep(.btn-next) {
  border-radius: 12px;
  min-width: 40px;
  height: 40px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #2c3e50 !important; /* 修复箭头颜色 */
  font-weight: 600;
}

.modern-pagination :deep(.btn-prev:hover),
.modern-pagination :deep(.btn-next:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
}

/* 响应式设计 */
@media (max-width: 768px) {
  .food-gallery-container {
    padding: 16px;
    /* 移动端也考虑滚动条空间，但通常移动端滚动条不占用空间 */
    padding-right: 16px;
    padding-left: 16px;
  }
  
  .title {
    font-size: 2rem;
  }
  
  .description {
    font-size: 1rem;
  }
  
  .ai-search-area {
    padding: 16px;
  }
  
  .ai-search-title {
    font-size: 1.3rem;
  }
  
  .suggested-queries {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* 自定义滚动动画 */
.fade-in-section {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-in-section.visible {
  opacity: 1;
  transform: translateY(0);
}

/* 加载动画增强 */
.recipe-grid-wrapper .el-row {
  animation: slideInGrid 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideInGrid {
  from {
    opacity: 0;
    transform: translateY(40px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 增强的背景渐变效果 - 与sparkles协调 */
.food-gallery-container::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.02) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.02) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(240, 147, 251, 0.02) 0%, transparent 50%),
    linear-gradient(-45deg, rgba(102, 126, 234, 0.01), rgba(118, 75, 162, 0.01), rgba(240, 147, 251, 0.01), rgba(245, 87, 108, 0.01));
  background-size: 300% 300%, 300% 300%, 300% 300%, 400% 400%;
  z-index: -2;
  animation: enhancedGradientFlow 25s ease-in-out infinite;
}

@keyframes enhancedGradientFlow {
  0%, 100% { 
    background-position: 0% 50%, 0% 50%, 0% 50%, 0% 50%; 
    opacity: 0.8;
  }
  25% { 
    background-position: 100% 50%, 20% 80%, 40% 40%, 25% 75%; 
    opacity: 1;
  }
  50% { 
    background-position: 50% 100%, 80% 20%, 60% 60%, 50% 50%; 
    opacity: 0.9;
  }
  75% { 
    background-position: 0% 50%, 60% 40%, 80% 20%, 75% 25%; 
    opacity: 1;
  }
}

/* 磁性悬停效果 */
.recipe-col {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.recipe-col:hover {
  transform: translateY(-8px) scale(1.03);
  filter: drop-shadow(0 16px 32px rgba(0, 0, 0, 0.15));
}

/* Sparkles 响应式和交互效果 */
@media (max-width: 768px) {
  .sparkle.large {
    width: 8px;
    height: 8px;
  }
  
  .sparkle.medium {
    width: 6px;
    height: 6px;
  }
  
  .sparkle.small {
    width: 3px;
    height: 3px;
  }
}

/* 暗色模式下的sparkles效果 */
@media (prefers-color-scheme: dark) {
  .sparkle-inner {
    background: radial-gradient(circle, rgba(255, 255, 255, 0.6) 0%, transparent 70%);
  }
  
  @keyframes sparkleGlow {
    0% {
      box-shadow: 0 0 8px rgba(102, 126, 234, 0.8), 0 0 16px rgba(118, 75, 162, 0.6);
      background: radial-gradient(circle, rgba(102, 126, 234, 0.9) 0%, transparent 70%);
    }
    25% {
      box-shadow: 0 0 10px rgba(240, 147, 251, 0.9), 0 0 20px rgba(245, 87, 108, 0.7);
      background: radial-gradient(circle, rgba(240, 147, 251, 0.9) 0%, transparent 70%);
    }
    50% {
      box-shadow: 0 0 12px rgba(245, 87, 108, 1), 0 0 24px rgba(102, 126, 234, 0.8);
      background: radial-gradient(circle, rgba(245, 87, 108, 0.9) 0%, transparent 70%);
    }
    75% {
      box-shadow: 0 0 10px rgba(118, 75, 162, 0.9), 0 0 20px rgba(240, 147, 251, 0.7);
      background: radial-gradient(circle, rgba(118, 75, 162, 0.9) 0%, transparent 70%);
    }
    100% {
      box-shadow: 0 0 8px rgba(102, 126, 234, 0.8), 0 0 16px rgba(118, 75, 162, 0.6);
      background: radial-gradient(circle, rgba(102, 126, 234, 0.9) 0%, transparent 70%);
    }
  }

  .ai-search-card {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
  }
  
  .search-result-info {
    background-color: rgba(102, 126, 234, 0.15);
  }
  
  /* 分页器暗色模式优化 */
  .modern-pagination :deep(.el-pager li) {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
    color: #ffffff !important;
    border-color: rgba(102, 126, 234, 0.3) !important;
    font-weight: 600;
  }
  
  .modern-pagination :deep(.el-pager li:hover) {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.4), rgba(118, 75, 162, 0.4)) !important;
    color: #ffffff !important;
  }
  
  .modern-pagination :deep(.btn-prev),
  .modern-pagination :deep(.btn-next) {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
    color: #ffffff !important;
    border-color: rgba(102, 126, 234, 0.3) !important;
    font-weight: 600;
  }
  
  .modern-pagination :deep(.el-pager li.is-active) {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: #ffffff !important;
  }
  
  .modern-pagination :deep(.btn-prev),
  .modern-pagination :deep(.btn-next) {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
    color: #ffffff !important;
    border-color: rgba(102, 126, 234, 0.3) !important;
  }
  
  .modern-pagination :deep(.btn-prev:hover),
  .modern-pagination :deep(.btn-next:hover) {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.4), rgba(118, 75, 162, 0.4)) !important;
    color: #ffffff !important;
  }
}

/* 全局滚动优化 - 防止双滚动条和布局跳动 */
.food-gallery-container * {
  /* 确保所有子元素不会产生不必要的滚动条 */
  box-sizing: border-box;
}

/* 响应式下的padding调整已合并到上面的样式中 */

/* Element Plus 组件滚动优化 */
.food-gallery-container :deep(.el-card),
.food-gallery-container :deep(.el-collapse),
.food-gallery-container :deep(.el-alert) {
  overflow: visible !important;
  max-height: none !important;
  height: auto !important;
}

.food-gallery-container :deep(.el-card__body) {
  overflow: visible !important;
  max-height: none !important;
  height: auto !important;
}

.food-gallery-container :deep(.el-collapse-item__content) {
  overflow: visible !important;
  max-height: none !important;
}

/* 确保加载状态不影响滚动 */
.food-gallery-container :deep(.el-loading-parent--relative) {
  overflow: visible !important;
}

/* 修复可能的容器高度问题 */
.food-gallery-container > * {
  flex-shrink: 0;
}

/* 确保页面滚动平滑 */
.food-gallery-container {
  scroll-behavior: smooth;
}

/* 优化滚动性能 */
.recipe-grid-wrapper,
.pagination-wrapper {
  contain: layout style paint;
  will-change: auto;
}

/* 确保分页区域始终可见 */
.pagination-wrapper {
  contain: layout;
  isolation: isolate;
}
</style>