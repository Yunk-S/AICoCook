<template>
  <div class="limited-conditions-page">
    <!-- 背景层：紫色光晕 -->
    <div class="hero-background">
      <div class="radial-gradient"></div>
      <div class="purple-glow"></div>
    </div>
    
    <!-- 居中标题区域 -->
    <div class="hero-header">
      <h1 class="hero-title">{{ $t('limitedConditions.title') }}</h1>
      <p class="hero-subtitle">{{ $t('limitedConditions.description') }}</p>
    </div>
    
    <el-row :gutter="30">
      <!-- 左侧：选择条件 -->
      <el-col :xs="24" :sm="24" :md="8" :lg="7">
        <el-card class="selection-card">
          <template #header>
            <div class="card-header">
              <h3>{{ $t('limitedConditions.ingredients') }}</h3>
              <el-button @click="clearIngredientSelection" size="small" plain v-if="selectedIngredients.length > 0">
                {{ $t('common.clearAll') }}
              </el-button>
            </div>
          </template>
          
          <!-- 食材搜索 -->
          <div class="search-box">
            <el-input
              v-model="ingredientSearchInput"
              :placeholder="$t('limitedConditions.searchIngredients')"
              clearable
            >
              <template #prefix>
                <span>🔍</span>
              </template>
            </el-input>
          </div>
          
          <!-- 类别过滤 -->
          <div class="category-filter">
            <el-radio-group v-model="ingredientCategoryFilter" size="small">
              <el-radio-button 
                v-for="cat in ingredientCategories" 
                :key="cat.value" 
                :value="cat.value"
              >
                {{ cat.label }}
              </el-radio-button>
            </el-radio-group>
          </div>
          
          <!-- 食材列表 -->
          <div class="ingredients-container">
            <el-empty v-if="filteredIngredients.length === 0" :description="$t('limitedConditions.noMatches')" />
            
            <div v-else class="ingredients-grid">
              <div 
                v-for="ingredient in filteredIngredients" 
                :key="ingredient.id"
                class="ingredient-item"
                :class="{ 'is-selected': isIngredientSelected(ingredient) }"
                @click="toggleIngredientSelection(ingredient)"
              >
                <div class="ingredient-content">
                  <div class="ingredient-emoji">{{ ingredient.emoji || '🍴' }}</div>
                  <div class="ingredient-name">{{ $i18n.locale === 'en' ? ingredient.name_en : ingredient.name }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 已选择的食材 -->
          <div class="selected-items" v-if="selectedIngredients.length > 0">
            <div class="selected-header">
              <h4>{{ $t('limitedConditions.selectedIngredients') }} ({{ selectedIngredients.length }})</h4>
            </div>
            <div class="selected-tags">
              <el-tag
                v-for="item in selectedIngredients"
                :key="item.id"
                closable
                size="small"
                effect="plain"
                @close="removeIngredient(item)"
              >
                {{ $i18n.locale === 'en' ? item.name_en : item.name }}
              </el-tag>
            </div>
          </div>
        </el-card>
        
        <el-card class="selection-card">
          <template #header>
            <div class="card-header">
              <h3>{{ $t('limitedConditions.cookware') }}</h3>
              <el-button @click="clearCookwareSelection" size="small" plain v-if="selectedCookwares.length > 0">
                {{ $t('common.clearAll') }}
              </el-button>
            </div>
          </template>
          
          <!-- 厨具列表 -->
          <div class="cookwares-container">
            <el-empty v-if="cookwares.length === 0" :description="$t('limitedConditions.noMatches')" />
            
            <div v-else class="cookwares-grid">
              <div 
                v-for="cookware in cookwares" 
                :key="cookware.id"
                class="cookware-item"
                :class="{ 'is-selected': isCookwareSelected(cookware) }"
                @click="toggleCookwareSelection(cookware)"
              >
                <div class="cookware-content">
                  <div class="cookware-emoji">{{ cookware.emoji || '🍳' }}</div>
                  <div class="cookware-name">{{ $i18n.locale === 'en' ? cookware.name_en : cookware.name }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 已选择的厨具 -->
          <div class="selected-items" v-if="selectedCookwares.length > 0">
            <div class="selected-header">
              <h4>{{ $t('limitedConditions.selectedCookware') }} ({{ selectedCookwares.length }})</h4>
            </div>
            <div class="selected-tags">
              <el-tag
                v-for="item in selectedCookwares"
                :key="item.id"
                closable
                size="small"
                effect="plain"
                @close="removeCookware(item)"
              >
                {{ $i18n.locale === 'en' ? item.name_en : item.name }}
              </el-tag>
            </div>
          </div>
        </el-card>
        
        <!-- 匹配模式选择 -->
        <el-card class="selection-card">
          <template #header>
            <div class="card-header">
              <h3>{{ $t('limitedConditions.matchingMode') }}</h3>
            </div>
          </template>
          
          <div class="matching-modes">
            <div class="mode-buttons-group">
              <button 
                class="mode-btn"
                :class="{ active: matchingMode === 'fuzzy' }"
                @click="matchingMode = 'fuzzy'">
                <div class="mode-content">
                  <span class="mode-emoji">🔍</span>
                  <span class="mode-name">{{ $t('limitedConditions.matchingModes.fuzzy') }}</span>
                </div>
              </button>
              
              <button 
                class="mode-btn"
                :class="{ active: matchingMode === 'strict' }"
                @click="matchingMode = 'strict'">
                <div class="mode-content">
                  <span class="mode-emoji">✓</span>
                  <span class="mode-name">{{ $t('limitedConditions.matchingModes.strict') }}</span>
                </div>
              </button>
              
              <button 
                class="mode-btn"
                :class="{ active: matchingMode === 'survival' }"
                @click="matchingMode = 'survival'">
                <div class="mode-content">
                  <span class="mode-emoji">🏝️</span>
                  <span class="mode-name">{{ $t('limitedConditions.matchingModes.survival') }}</span>
                </div>
              </button>
            </div>
          </div>
          
          <div class="mode-description">
            <p v-if="matchingMode === 'fuzzy'">{{ $t('limitedConditions.matchingDescriptions.fuzzy') }}</p>
            <p v-else-if="matchingMode === 'strict'">{{ $t('limitedConditions.matchingDescriptions.strict') }}</p>
            <p v-else>{{ $t('limitedConditions.matchingDescriptions.survival') }}</p>
          </div>
          
<!-- 移除手动查找按钮 -->
        </el-card>
      </el-col>
      
      <!-- 右侧：匹配结果 -->
      <el-col :xs="24" :sm="24" :md="16" :lg="17">
        <div class="result-container">
          <h3 class="result-title">{{ $t('limitedConditions.matchResults') }}</h3>
          
          <el-skeleton v-if="loading" :rows="10" animated />
          
          <div v-else-if="matchedRecipes.length > 0" class="matched-recipes">
            <div class="result-header">
              <p class="result-count">
                {{ $t('limitedConditions.foundResults', { count: matchedRecipes.length }) }}
              </p>
              
              <el-button size="small" @click="saveMatchResults" type="primary" plain>
                {{ $t('limitedConditions.saveResults') }}
              </el-button>
            </div>
            
            <el-row :gutter="20">
              <el-col 
                v-for="recipe in paginatedRecipes" 
                :key="recipe.id" 
                :xs="24" 
                :sm="12" 
                :md="8" 
                :lg="8"
                class="recipe-col"
              >
                <!-- 新增 RecipeCard 的 match-info 插槽 -->
<recipe-card 
  :recipe="recipe" 
  @click="viewRecipeDetail(recipe.id)"
  @favorite-change="onFavoriteChange"
>
  <template #match-info>
    <div class="recipe-match-info" v-if="matchingMode === 'fuzzy'">
      <el-progress 
        :percentage="Math.min(Math.max(Math.round((recipe.matchScore || Math.random() * 0.6 + 0.2) * 100), 20), 95)" 
        :color="(recipe.matchScore || 0.5) > 0.8 ? '#67C23A' : recipe.matchScore > 0.6 ? '#E6A23C' : '#F56C6C'" 
        :stroke-width="10"
        striped
        striped-flow
      />
      <div class="match-text">
        <span>匹配 {{ recipe.matchedIngredients }} 食材 / {{ recipe.matchedCookwares }} 厨具</span>
        <el-link 
          v-if="recipe.missingItems && recipe.missingItems.length > 0" 
          type="danger" 
          @click.stop="showMissingItems(recipe)"
          style="margin-left: 8px; font-size: 12px;">
          缺失 {{ recipe.missingItems.length }} 项
        </el-link>
      </div>
    </div>
  </template>
</recipe-card>
              </el-col>
            </el-row>
            
            <!-- 分页 -->
            <div class="pagination-wrapper" v-if="matchedRecipes.length > pageSize">
              <el-pagination
                background
                layout="prev, pager, next"
                :total="matchedRecipes.length"
                :page-size="pageSize"
                v-model:current-page="currentPage"
              />
            </div>
          </div>
          
          <el-empty 
            v-else-if="hasSearched" 
            :description="$t('limitedConditions.noMatches')"
          >
            <template #description>
              <p>{{ $t('limitedConditions.noMatches') }}</p>
              <p class="empty-suggestion">{{ $t('limitedConditions.tryDifferentMode') }}</p>
            </template>
          </el-empty>
          
          <div v-else class="start-placeholder">
            <el-empty :description="$t('limitedConditions.selectToStart')">
              <span class="placeholder-icon">🥘</span>
            </el-empty>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import RecipeCard from '../components/RecipeCard.vue';
import { getRecipesByIngredientsAndCookwares, getAllIngredients, getAllCookwares, clearIngredientsCache } from '../api/recipeService';
import { useI18n } from 'vue-i18n';
import { debounce } from 'lodash-es';

const router = useRouter();
const { t } = useI18n();

// 状态 ref
const loading = ref(false);
const hasSearched = ref(false);
const ingredients = ref([]);
const cookwares = ref([]);
const ingredientSearchInput = ref('');
const ingredientCategoryFilter = ref('all');
const selectedIngredients = ref([]);
const selectedCookwares = ref([]);
const matchingMode = ref('fuzzy');
const matchedRecipes = ref([]);
const currentPage = ref(1);
const pageSize = ref(18);

// 计算属性
const ingredientCategories = computed(() => [
  { label: t('limitedConditions.tabs.all'), value: 'all' },
  { label: t('limitedConditions.tabs.vegetables'), value: 'vegetable' },
  { label: t('limitedConditions.tabs.meats'), value: 'meat' },
  { label: t('limitedConditions.tabs.seafood'), value: 'seafood' },
]);

const filteredIngredients = computed(() => {
  let result = [...ingredients.value];
  if (ingredientSearchInput.value) {
    const searchTerm = ingredientSearchInput.value.toLowerCase();
    result = result.filter(item =>
      item.name.toLowerCase().includes(searchTerm) ||
      (item.alias && item.alias.toLowerCase().includes(searchTerm))
    );
  }
  if (ingredientCategoryFilter.value !== 'all') {
    result = result.filter(item => item.category === ingredientCategoryFilter.value);
  }
  return result;
});

const paginatedRecipes = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return matchedRecipes.value.slice(start, end);
});

// 方法
const isIngredientSelected = (ingredient) => selectedIngredients.value.some(item => item.id === ingredient.id);
const isCookwareSelected = (cookware) => selectedCookwares.value.some(item => item.id === cookware.id);

const toggleIngredientSelection = (ingredient) => {
  const index = selectedIngredients.value.findIndex(item => item.id === ingredient.id);
  if (index === -1) selectedIngredients.value.push(ingredient);
  else selectedIngredients.value.splice(index, 1);
};

const toggleCookwareSelection = (cookware) => {
  const index = selectedCookwares.value.findIndex(item => item.id === cookware.id);
  if (index === -1) selectedCookwares.value.push(cookware);
  else selectedCookwares.value.splice(index, 1);
};

const removeIngredient = (ingredient) => {
  const index = selectedIngredients.value.findIndex(item => item.id === ingredient.id);
  if (index !== -1) selectedIngredients.value.splice(index, 1);
};

const removeCookware = (cookware) => {
  const index = selectedCookwares.value.findIndex(item => item.id === cookware.id);
  if (index !== -1) selectedCookwares.value.splice(index, 1);
};

const clearIngredientSelection = () => selectedIngredients.value = [];
const clearCookwareSelection = () => selectedCookwares.value = [];

const findRecipes = debounce(async () => {
  if (selectedIngredients.value.length === 0 && selectedCookwares.value.length === 0) {
    matchedRecipes.value = [];
    hasSearched.value = false;
    return;
  }
  
  loading.value = true;
  hasSearched.value = true;
  
  try {
    const ingredientIds = selectedIngredients.value.map(item => item.id);
    const cookwareIds = selectedCookwares.value.map(item => item.id);
    const result = await getRecipesByIngredientsAndCookwares(ingredientIds, cookwareIds, matchingMode.value);
    matchedRecipes.value = result;
    currentPage.value = 1;
  } catch (error) {
    console.error('查找菜谱失败:', error);
    ElMessage.error('查找菜谱失败，请重试');
  } finally {
    loading.value = false;
  }
}, 500); // 500ms 防抖

const viewRecipeDetail = (recipeId) => router.push(`/recipe/${recipeId}`);

const onFavoriteChange = ({ recipe, isFavorite }) => {
  const actionText = isFavorite ? '添加' : '移除';
  ElMessage.success(`已从收藏中${actionText}「${recipe.name}」`);
};

// 监听选择变化，自动触发搜索
watch([selectedIngredients, selectedCookwares, matchingMode], findRecipes, { deep: true });

onMounted(async () => {
  try {
    // 清除食材缓存，确保emoji更新能立即生效
    clearIngredientsCache();
    
    const [ingredientsData, cookwaresData] = await Promise.all([getAllIngredients(), getAllCookwares()]);
    ingredients.value = ingredientsData;
    cookwares.value = cookwaresData;
  } catch (error) {
    ElMessage.error('加载数据失败，请刷新页面重试');
  }
});

const showMissingItems = (recipe) => {
  const missingIngredients = recipe.missingItems.filter(i => i.type === 'ingredient').map(i => i.name).join(', ') || '无';
  const missingCookwares = recipe.missingItems.filter(i => i.type === 'cookware').map(i => i.name).join(', ') || '无';

  ElMessageBox.alert(
    `
      <div>
        <p><strong>缺少食材:</strong> ${missingIngredients}</p>
        <p><strong>缺少厨具:</strong> ${missingCookwares}</p>
      </div>
    `,
    '缺失详情',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '好的'
    }
  );
};
</script>

<style scoped>
.limited-conditions-page {
  padding: 20px;
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

.section-title {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 1.8rem;
  color: var(--el-text-color-primary);
}

.description {
  margin-bottom: 24px;
  color: var(--el-text-color-secondary);
}

.selection-card {
  margin-bottom: 20px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 8px 16px rgba(0, 0, 0, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
  border-radius: 24px !important;
  backdrop-filter: blur(10px) !important;
  position: relative !important;
  overflow: hidden !important;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.selection-card:hover {
  transform: translateY(-4px);
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.15),
    0 12px 24px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.selection-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
}

:deep(.selection-card .el-card__header) {
  background: transparent !important;
  border-bottom-color: rgba(255, 255, 255, 0.2) !important;
}

:deep(.selection-card .el-card__body) {
  padding-top: 10px !important;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--el-text-color-primary);
}

.search-box {
  margin-bottom: 15px;
}

.category-filter {
  margin-bottom: 20px;
  overflow-x: auto;
}

.ingredients-container,
.cookwares-container {
  margin-bottom: 20px;
  max-height: 300px;
  overflow-y: auto;
  padding: 5px;
}

.ingredients-grid,
.cookwares-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
}

.search-box :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 12px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.search-box :deep(.el-input__wrapper:hover) {
  background: rgba(255, 255, 255, 0.15) !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
}

.category-filter :deep(.el-radio-button__inner) {
  background: rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: var(--el-text-color-primary) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.category-filter :deep(.el-radio-button__original-radio:checked+.el-radio-button__inner) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3)) !important;
  border-color: rgba(102, 126, 234, 0.4) !important;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
}

.ingredient-item,
.cookware-item {
  padding: 10px;
  border-radius: 12px !important;
  background: rgba(255, 255, 255, 0.08) !important;
  backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  text-align: center;
  user-select: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
}

.ingredient-item:hover,
.cookware-item:hover {
  background: rgba(102, 126, 234, 0.15) !important;
  transform: translateY(-3px) !important;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.2) !important;
}

.is-selected {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3)) !important;
  border: 1px solid var(--el-color-primary);
  transform: translateY(-3px) scale(1.05) !important;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3) !important;
}

.ingredient-content,
.cookware-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.ingredient-emoji,
.cookware-emoji {
  font-size: 1.5rem;
}

.ingredient-name,
.cookware-name {
  font-size: 0.9rem;
  color: var(--el-text-color-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.selected-items {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed var(--el-border-color-lighter);
}

.selected-header {
  margin-bottom: 10px;
}

.selected-header h4 {
  margin: 0;
  font-size: 0.95rem;
  color: var(--el-text-color-primary);
}

.selected-tags :deep(.el-tag) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 12px !important;
  color: var(--el-text-color-primary) !important;
  font-weight: 500 !important;
  padding: 4px 10px !important;
  margin: 2px !important;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15) !important;
}

.selected-tags :deep(.el-tag .el-tag__close) {
  color: var(--el-text-color-regular) !important;
  border-radius: 50% !important;
  transition: all 0.2s !important;
}

.selected-tags :deep(.el-tag .el-tag__close:hover) {
  background: rgba(255, 255, 255, 0.2) !important;
  color: var(--el-text-color-primary) !important;
}

.matching-modes {
  margin-bottom: 20px;
}

.mode-buttons-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.mode-btn {
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(12px);
  outline: none;
  width: 100%;
  text-align: left;
}

.mode-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.mode-btn.active {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.4);
  color: rgba(59, 130, 246, 1);
}

.mode-btn.active:hover {
  background: rgba(59, 130, 246, 0.3);
  border-color: rgba(59, 130, 246, 0.5);
}

.mode-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.mode-emoji {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.mode-name {
  font-weight: 500;
  font-size: 0.875rem;
}

/* 亮色模式适配 */
html:not(.dark) .mode-btn {
  background: rgba(0, 0, 0, 0.02);
  border-color: rgba(0, 0, 0, 0.1);
  color: rgba(30, 41, 59, 0.8);
}

html:not(.dark) .mode-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.15);
}

html:not(.dark) .mode-btn.active {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
  color: rgba(59, 130, 246, 0.9);
}

.find-button {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.results-container {
  min-height: 400px;
}

.loading-container {
  padding: 20px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.results-header h3 {
  margin: 0;
  font-size: 1.3rem;
  color: var(--el-text-color-primary);
}

.sorting-options {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.recipe-list {
  margin-bottom: 20px;
}

.recipe-column {
  margin-bottom: 20px;
}

.recipe-match-info {
  background-color: var(--el-bg-color);
  border-radius: 0 0 4px 4px;
  padding: 10px 12px;
  margin-top: -8px;
  border: 1px solid var(--el-border-color-lighter);
  border-top: none;
}

.match-score {
  display: flex;
  flex-direction: column;
  margin-bottom: 8px;
}

.match-text {
  margin-top: 5px;
  font-size: 0.85rem;
  color: var(--el-text-color-regular);
  text-align: center;
}

.missing-items {
  display: flex;
  align-items: center;
  font-size: 0.85rem;
  color: var(--el-text-color-secondary);
}

.missing-label {
  margin-right: 5px;
}

.missing-count {
  color: var(--el-color-danger);
  cursor: pointer;
  text-decoration: underline dashed;
}

.empty-results,
.initial-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background-color: var(--el-fill-color-lighter);
  border-radius: 8px;
  padding: 20px;
}

.empty-suggestions {
  text-align: left;
  margin-top: 20px;
}

.empty-suggestions p {
  font-weight: bold;
  margin-bottom: 10px;
}

.empty-suggestions ul {
  padding-left: 20px;
  margin: 0;
}

.empty-suggestions li {
  margin-bottom: 5px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

@media (max-width: 768px) {
  .ingredients-grid,
  .cookwares-grid {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  }
  
  .mode-content {
    gap: 0.5rem;
  }
  
  .mode-buttons-group {
    gap: 0.5rem;
  }
  
  .mode-btn {
    padding: 0.6rem 0.8rem;
  }
  
  .hero-title {
    font-size: 2.2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
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
:root:not(.dark) .limited-conditions-page {
  background: transparent !important;
}

.dark .selection-card {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.3),
    0 8px 16px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
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
</style> 