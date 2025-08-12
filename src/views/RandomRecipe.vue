<template>
  <div class="random-recipe-page">
    <!-- 背景层：紫色光晕 -->
    <div class="hero-background">
      <div class="radial-gradient"></div>
      <div class="purple-glow"></div>
    </div>
    
    <!-- 居中标题区域 -->
    <div class="hero-header">
      <h1 class="hero-title">{{ t('randomRecipe.title') }}</h1>
      <p class="hero-subtitle">{{ t('randomRecipe.description') }}</p>
    </div>
    
    <!-- 按钮并排区域 -->
    <div class="action-container">
      <button 
        class="random-btn primary-btn"
        @click="generateRandomMeal" 
        :disabled="loading"
      >
        <span v-if="loading" class="loading-spinner">⏳</span>
        <span v-else>🔄</span>
        {{ t('randomRecipe.refreshButton') }}
      </button>
      
      <button 
        v-if="mealCombination" 
        class="random-btn save-btn" 
        @click="saveMealToHistory"
      >
        {{ t('randomRecipe.saveMeal') }}
      </button>
    </div>
    
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
    
    <div v-else-if="mealCombination" class="recipes-container">
      
      <!-- 餐单菜谱列表 -->
      <el-row :gutter="20" class="recipe-list">
        <el-col 
          v-for="recipe in mealCombination.recipes" 
          :key="recipe.id" 
          :xs="24" 
          :sm="12" 
          :md="8" 
          :lg="6"
          class="recipe-column"
        >
          <recipe-card 
            :recipe="recipe" 
            @click="viewRecipeDetail(recipe.id)"
            @favorite-change="onFavoriteChange"
          />
        </el-col>
      </el-row>
      
      <!-- 历史记录 - 透明背景 -->
      <div v-if="mealHistory.length > 0" class="history-section">
        <div class="history-header">
          <h3>{{ t('randomRecipe.mealHistory') }}</h3>
          <button class="random-btn danger-btn" @click="clearHistory">
            {{ t('common.clearAll') }}
          </button>
        </div>
        
        <div class="history-scroller" role="list">
          <div 
            v-for="meal in mealHistory"
            :key="meal.id"
            class="history-card glass-card"
            role="listitem"
          >
            <div class="history-card-top">
              <div class="history-meta" @click="loadHistoryMeal(meal)">
                <span class="history-date">{{ formatDate(meal.createdAt) }}</span>
              </div>
              <div class="actions">
                <button class="random-btn text-btn sm" @click="loadHistoryMeal(meal)">
                  {{ t('randomRecipe.loadMeal') }}
                </button>
                <button class="random-btn text-btn sm danger" @click="deleteHistoryMeal(meal.id)">
                  {{ t('randomRecipe.deleteMeal') }}
                </button>
              </div>
            </div>

            <div class="thumb-grid">
              <div 
                v-for="recipe in meal.recipes.slice(0,4)"
                :key="recipe.id"
                class="thumb"
                @click.stop="viewRecipeDetail(recipe.id)"
              >
                <el-tooltip :content="recipe.name" placement="top">
                  <img 
                    :src="recipe.image || '/images/recipe-placeholder.jpg'" 
                    :alt="recipe.name"
                  />
                </el-tooltip>
              </div>
            </div>

            <div class="name-chips" :title="meal.recipes.map(r=>r.name).join('、')">
              <span v-for="recipe in meal.recipes.slice(0,3)" :key="recipe.id" class="chip">
                {{ recipe.name }}
              </span>
              <span v-if="meal.recipes.length > 3" class="chip more">+{{ meal.recipes.length - 3 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="empty-state">
      <el-empty :description="t('randomRecipe.emptyState')">
        <button class="random-btn primary-btn" @click="generateRandomMeal">
          {{ t('randomRecipe.tryNow') }}
        </button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useI18n } from 'vue-i18n';
import RecipeCard from '../components/RecipeCard.vue';
import { getRandomMealCombination } from '../api/recipeService';
import { formatDate } from '../utils/helpers';

const router = useRouter();
const { t } = useI18n();
const loading = ref(false);
const mealCombination = ref(null);
const mealHistory = ref([]);

// 获取随机菜单
const generateRandomMeal = async () => {
  loading.value = true;
  try {
    mealCombination.value = await getRandomMealCombination();
  } catch (error) {
    console.error('生成随机菜单失败:', error);
    ElMessage.error(t('randomRecipe.generateError'));
  } finally {
    loading.value = false;
  }
};

// 保存菜单到历史记录
const saveMealToHistory = async () => {
  if (!mealCombination.value) return;
  
  try {
    const historyItem = {
      id: `meal-${Date.now()}`,
      createdAt: new Date().toISOString(),
      recipes: mealCombination.value.recipes.map(recipe => ({
        id: recipe.id,
        name: recipe.name,
        image: recipe.image,
        nutrition: recipe.nutrition,
        difficulty: recipe.difficulty,
      }))
    };
    
    mealHistory.value.unshift(historyItem);
    
    if (mealHistory.value.length > 10) {
      mealHistory.value.pop();
    }
    
    localStorage.setItem('mealCombinationHistory', JSON.stringify(mealHistory.value));
    
    ElMessage.success(t('randomRecipe.saveSuccess'));
  } catch (error) {
    console.error('保存历史记录失败:', error);
    ElMessage.error(t('randomRecipe.saveError'));
  }
};

const clearHistory = () => {
  ElMessageBox.confirm(
    t('randomRecipe.confirmClearHistory'),
    t('common.warning'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
      customClass: 'custom-message-box',
      showClose: true,
      closeOnClickModal: false,
      closeOnPressEscape: true,
    }
  )
  .then(() => {
    mealHistory.value = [];
    localStorage.removeItem('mealCombinationHistory');
    ElMessage.success(t('randomRecipe.clearSuccess'));
    generateRandomMeal();
  })
  .catch(() => {
    // 用户取消操作
  });
};

// 加载历史菜单
const loadHistoryMeal = (historyItem) => {
  if (!historyItem || !historyItem.recipes) return;
  
  mealCombination.value = {
    id: historyItem.id,
    recipes: historyItem.recipes,
    createdAt: new Date(historyItem.createdAt)
  };
  ElMessage.info(t('randomRecipe.loadSuccess'));
};

// 查看菜谱详情
const viewRecipeDetail = (recipeId) => {
  if (recipeId) {
    router.push(`/recipe/${recipeId}`);
  }
};

// 收藏状态改变
const onFavoriteChange = ({ recipe, isFavorite }) => {
  const actionText = isFavorite ? t('common.addedTo') : t('common.removedFrom');
  ElMessage.success(`「${recipe.name}」${actionText}${t('common.favorites')}`);
};

// 计算平均难度
const averageDifficulty = computed(() => {
  if (!mealCombination.value || !mealCombination.value.recipes || mealCombination.value.recipes.length === 0) {
    return t('difficulties.unknown');
  }
  
  const difficultyMap = { 'easy': 1, 'medium': 2, 'hard': 3 };
  const difficultySum = mealCombination.value.recipes.reduce((sum, recipe) => {
    return sum + (difficultyMap[recipe.difficulty] || 2);
  }, 0);
  
  const avgDifficulty = difficultySum / mealCombination.value.recipes.length;
  
  if (avgDifficulty <= 1.5) return t('difficulties.easy');
  if (avgDifficulty <= 2.5) return t('difficulties.medium');
  return t('difficulties.hard');
});

// 删除单个历史组合
const deleteHistoryMeal = (mealId) => {
  const targetIndex = mealHistory.value.findIndex(item => item.id === mealId);
  if (targetIndex === -1) return;

  ElMessageBox.confirm(
    t('randomRecipe.confirmDeleteMeal'),
    t('common.warning'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
      customClass: 'custom-message-box',
      showClose: true,
      closeOnClickModal: false,
      closeOnPressEscape: true,
    }
  ).then(() => {
    mealHistory.value.splice(targetIndex, 1);
    localStorage.setItem('mealCombinationHistory', JSON.stringify(mealHistory.value));
    ElMessage.success(t('randomRecipe.deleteSuccess'));
  }).catch(() => {});
};

// 加载历史记录
const loadMealHistoryFromStorage = () => {
  try {
    const historyData = localStorage.getItem('mealCombinationHistory');
    if (historyData) {
      mealHistory.value = JSON.parse(historyData).map(item => ({
        ...item,
        createdAt: new Date(item.createdAt)
      }));
    }
  } catch (error) {
    console.error('加载历史记录失败:', error);
    ElMessage.error(t('randomRecipe.loadHistoryError'));
  }
};

onMounted(() => {
  loadMealHistoryFromStorage();
  if (mealHistory.value.length === 0) {
    generateRandomMeal();
  } else {
    loadHistoryMeal(mealHistory.value[0]);
  }
});
</script>

<style scoped>
.random-recipe-page {
  padding: 24px;
}
/* 居中标题样式 */
.hero-header {
  text-align: center;
  margin-bottom: 48px;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin: 0 0 16px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.2rem;
  color: var(--el-text-color-secondary);
  margin: 0;
}

/* 按钮并排布局 */
.action-container {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 32px;
}
.meal-container {
  margin-bottom: 32px;
}
/* 历史区域样式 - 透明背景 */
.history-section {
  margin-top: 48px;
  padding: 0;
  background: transparent;
  border: none;
}

/* 横向滚动容器 */
.history-scroller {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: minmax(320px, 380px);
  gap: 20px;
  padding-bottom: 8px;
  overflow-x: auto;
  overscroll-behavior-x: contain;
  scroll-snap-type: x mandatory;
}

.history-scroller::-webkit-scrollbar {
  height: 8px;
}

.history-scroller::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
}

/* 卡片与毛玻璃效果 */
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
}

html:not(.dark) .glass-card {
  background: rgba(0, 0, 0, 0.03);
  border-color: rgba(0, 0, 0, 0.08);
}

.history-card {
  scroll-snap-align: start;
  border-radius: 16px;
  padding: 16px;
  transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}

.history-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,.18);
  border-color: rgba(255,255,255,.22);
}

.history-card-top {
  display: grid;
  grid-template-columns: 1fr auto auto;
  align-items: center;
  column-gap: 10px;
  margin-bottom: 12px;
}

.actions { display: inline-flex; gap: 8px; }
.random-btn.text-btn.sm.danger { color: rgba(239,68,68,0.9); }
.random-btn.text-btn.sm.danger:hover { background: rgba(239,68,68,0.12); }

.history-meta { 
  display: inline-flex; 
  align-items: center; 
  gap: 10px; 
  cursor: pointer;
}

.history-date { 
  font-weight: 600; 
  color: var(--el-text-color-primary);
}

.history-badge { 
  font-size: 12px; 
  padding: 2px 8px; 
  border-radius: 999px; 
  background: rgba(59,130,246,.15); 
  color: #60a5fa; 
  border: 1px solid rgba(59,130,246,.25);
}

.random-btn.text-btn.sm { 
  padding: 6px 10px; 
  font-size: 12px;
}

/* 3x2 缩略图栅格 */
.thumb-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.thumb img {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid var(--el-border-color-lighter);
}

.name-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.chip {
  max-width: 60%;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(255,255,255,.06);
  border: 1px solid rgba(255,255,255,.15);
  color: var(--el-text-color-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.more { 
  background: rgba(99,102,241,.15); 
  color: #a5b4fc; 
  border-color: rgba(99,102,241,.25);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.history-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
/* 移除不再使用的样式 */
.recipe-list {
  margin-bottom: 24px;
}
.recipe-column {
  margin-bottom: 20px;
}
.nutrition-chart {
  padding: 16px;
}
.chart-container {
  display: flex;
  align-items: center;
  gap: 32px;
}
.calories-circle {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background-color: var(--el-color-primary-light-9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 4px solid var(--el-color-primary-light-5);
}
.calories-value {
  font-size: 2rem;
  font-weight: bold;
  color: var(--el-color-primary);
}
.calories-label {
  font-size: 1rem;
  color: var(--el-text-color-secondary);
}
.nutrition-bars {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.nutrition-item {
  display: grid;
  grid-template-columns: 80px 1fr 50px;
  align-items: center;
  gap: 12px;
}
.nutrition-label {
  font-size: 0.9rem;
  color: var(--el-text-color-regular);
  text-align: right;
}
.nutrition-value {
  font-size: 0.9rem;
  font-weight: bold;
  color: var(--el-text-color-primary);
}
.history-card {
  background-color: var(--el-bg-color-page);
}
.history-meal-card {
  background-color: var(--el-bg-color-overlay);
  border-radius: 8px;
  padding: 16px;
  height: 100%;
  border: 1px solid var(--el-border-color-light);
  transition: box-shadow 0.3s;
}
.history-meal-card:hover {
  box-shadow: var(--el-box-shadow-light);
}
.history-meal-header {
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}
.history-meal-date {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: var(--el-text-color-primary);
}
.history-meal-recipes {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}
.history-recipe-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  overflow: hidden;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: background-color 0.2s;
}
.history-recipe-item:hover {
  background-color: var(--el-fill-color-lighter);
}
.history-recipe-image {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid var(--el-border-color-lighter);
}
.history-recipe-name {
  font-size: 0.75rem;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--el-text-color-secondary);
  width: 100%;
}
.empty-state {
  padding: 40px 0;
}

/* 毛玻璃按钮样式 */
.random-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(12px);
  outline: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.random-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.random-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.random-btn.primary-btn {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.4);
  color: rgba(59, 130, 246, 1);
  font-size: 1rem;
  padding: 1rem 2rem;
}

.random-btn.primary-btn:hover {
  background: rgba(59, 130, 246, 0.3);
  border-color: rgba(59, 130, 246, 0.5);
}

.random-btn.secondary-btn {
  background: rgba(168, 85, 247, 0.1);
  border-color: rgba(168, 85, 247, 0.3);
  color: rgba(168, 85, 247, 0.9);
}

.random-btn.secondary-btn:hover {
  background: rgba(168, 85, 247, 0.2);
  border-color: rgba(168, 85, 247, 0.5);
}

.random-btn.save-btn {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
  color: rgba(34, 197, 94, 0.9);
}

.random-btn.save-btn:hover {
  background: rgba(34, 197, 94, 0.2);
  border-color: rgba(34, 197, 94, 0.5);
}

.random-btn.danger-btn {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: rgba(239, 68, 68, 0.9);
}

.random-btn.danger-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.5);
}

.random-btn.text-btn {
  background: transparent;
  border: none;
  color: rgba(59, 130, 246, 0.8);
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
}

.random-btn.text-btn:hover {
  background: rgba(59, 130, 246, 0.1);
  color: rgba(59, 130, 246, 1);
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 亮色模式适配 */
html:not(.dark) .random-btn {
  background: rgba(0, 0, 0, 0.02);
  border-color: rgba(0, 0, 0, 0.1);
  color: rgba(30, 41, 59, 0.9);
}

html:not(.dark) .random-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.15);
}

html:not(.dark) .random-btn.primary-btn {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
  color: rgba(59, 130, 246, 0.9);
}

html:not(.dark) .random-btn.secondary-btn {
  background: rgba(168, 85, 247, 0.1);
  border-color: rgba(168, 85, 247, 0.3);
  color: rgba(168, 85, 247, 0.9);
}

html:not(.dark) .random-btn.save-btn {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
  color: rgba(34, 197, 94, 0.9);
}

html:not(.dark) .random-btn.danger-btn {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: rgba(239, 68, 68, 0.9);
}

html:not(.dark) .random-btn.text-btn {
  background: transparent;
  color: rgba(59, 130, 246, 0.8);
}

/* 背景层样式 - 与Home页面一致 */
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
:root:not(.dark) .random-recipe-page {
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
      rgba(59, 130, 246, 0.06), 
      transparent 50%
    ),
    radial-gradient(
      ellipse 60% 40% at 50% 50%, 
      rgba(236, 72, 153, 0.05), 
      transparent 50%
    );
  opacity: 0.7;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .action-container {
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }
  
  .chart-container {
    flex-direction: column;
  }
  
  .random-btn {
    padding: 0.6rem 1.2rem;
    font-size: 0.8rem;
  }
  
  .random-btn.primary-btn {
    padding: 0.8rem 1.6rem;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 1.8rem;
  }
  
  .hero-subtitle {
    font-size: 0.9rem;
  }
}
</style>

<style>
/* 自定义确认对话框样式 */
.custom-message-box {
  border-radius: 16px !important;
  backdrop-filter: blur(20px) !important;
  background: rgba(255, 255, 255, 0.95) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    0 2px 8px rgba(0, 0, 0, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
  overflow: hidden !important;
}

/* 深色模式下的对话框 */
.dark .custom-message-box {
  background: rgba(31, 41, 55, 0.95) !important;
  border: 1px solid rgba(75, 85, 99, 0.3) !important;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    0 2px 8px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
}

/* 对话框头部 */
.custom-message-box .el-message-box__header {
  padding: 24px 24px 16px 24px !important;
  border-bottom: 1px solid rgba(229, 231, 235, 0.3) !important;
}

.dark .custom-message-box .el-message-box__header {
  border-bottom: 1px solid rgba(75, 85, 99, 0.3) !important;
}

.custom-message-box .el-message-box__title {
  font-size: 1.25rem !important;
  font-weight: 600 !important;
  color: var(--el-text-color-primary) !important;
}

/* 对话框内容 */
.custom-message-box .el-message-box__content {
  padding: 20px 24px !important;
}

.custom-message-box .el-message-box__message {
  font-size: 1rem !important;
  line-height: 1.6 !important;
  color: var(--el-text-color-regular) !important;
}

/* 对话框底部按钮区域 */
.custom-message-box .el-message-box__btns {
  padding: 16px 24px 24px 24px !important;
  border-top: 1px solid rgba(229, 231, 235, 0.3) !important;
  background: transparent !important;
  text-align: right !important;
}

.dark .custom-message-box .el-message-box__btns {
  border-top: 1px solid rgba(75, 85, 99, 0.3) !important;
}

/* 毛玻璃按钮样式 */
.custom-message-box .el-button {
  border-radius: 10px !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  font-weight: 500 !important;
  padding: 10px 20px !important;
  margin-left: 12px !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
}

/* 取消按钮 */
.custom-message-box .el-button--default {
  background: rgba(107, 114, 128, 0.1) !important;
  color: var(--el-text-color-regular) !important;
  border-color: rgba(107, 114, 128, 0.2) !important;
}

.custom-message-box .el-button--default:hover {
  background: rgba(107, 114, 128, 0.2) !important;
  border-color: rgba(107, 114, 128, 0.3) !important;
  transform: translateY(-1px) !important;
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
}

/* 确认按钮 */
.custom-message-box .el-button--primary {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.9), rgba(220, 38, 38, 0.9)) !important;
  color: white !important;
  border-color: rgba(239, 68, 68, 0.4) !important;
}

.custom-message-box .el-button--primary:hover {
  background: linear-gradient(135deg, rgba(239, 68, 68, 1), rgba(220, 38, 38, 1)) !important;
  border-color: rgba(239, 68, 68, 0.6) !important;
  transform: translateY(-1px) !important;
  box-shadow: 
    0 4px 12px rgba(239, 68, 68, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
}

/* 深色模式下的按钮 */
.dark .custom-message-box .el-button--default {
  background: rgba(75, 85, 99, 0.3) !important;
  border-color: rgba(75, 85, 99, 0.4) !important;
}

.dark .custom-message-box .el-button--default:hover {
  background: rgba(75, 85, 99, 0.5) !important;
  border-color: rgba(75, 85, 99, 0.6) !important;
}

/* 关闭按钮 */
.custom-message-box .el-message-box__headerbtn {
  top: 20px !important;
  right: 20px !important;
  width: 32px !important;
  height: 32px !important;
  border-radius: 8px !important;
  background: rgba(107, 114, 128, 0.1) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(107, 114, 128, 0.2) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.custom-message-box .el-message-box__headerbtn:hover {
  background: rgba(107, 114, 128, 0.2) !important;
  border-color: rgba(107, 114, 128, 0.3) !important;
  transform: scale(1.05) !important;
}

.custom-message-box .el-message-box__close {
  font-size: 16px !important;
  color: var(--el-text-color-regular) !important;
}

/* 警告图标美化 */
.custom-message-box .el-message-box__status {
  font-size: 24px !important;
  margin-right: 12px !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .custom-message-box {
    margin: 20px !important;
    width: calc(100% - 40px) !important;
  }
  
  .custom-message-box .el-message-box__btns {
    flex-direction: column !important;
  }
  
  .custom-message-box .el-button {
    margin: 6px 0 !important;
    width: 100% !important;
  }
}
</style> 