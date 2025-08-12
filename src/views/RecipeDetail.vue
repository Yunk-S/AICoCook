<template>
  <div class="recipe-detail">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton animated :rows="10" />
    </div>
    
    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <el-result
        icon="error"
        :title="$t('recipeDetail.errorTitle')"
        :sub-title="$t('recipeDetail.errorSubtitle')"
      >
        <template #extra>
          <el-button type="primary" @click="goBack">
            {{ $t('common.goBack') }}
          </el-button>
        </template>
      </el-result>
    </div>
    
    <!-- 菜谱详情 -->
    <div v-else-if="recipe" class="recipe-content">
      <!-- 返回按钮 -->
      <div class="back-navigation">
        <el-button @click="goBack" link>
          ← {{ $t('common.goBack') }}
        </el-button>
      </div>
      
      <!-- 菜谱头部 -->
      <div class="recipe-header">
        <div class="recipe-title-container">
          <h1 class="recipe-title">{{ recipe.name }}</h1>
          
          <div class="recipe-actions">
            <el-button 
              :class="['favorite-button', {'is-favorite': isFavorite}]" 
              @click="toggleFavorite"
              circle
            >
              <span v-if="isFavorite">❤️</span>
              <span v-else>🤍</span>
            </el-button>
          </div>
        </div>
        
        <p v-if="recipe.description" class="recipe-description">
          {{ recipe.description }}
        </p>
        
        <!-- 标签和元数据 -->
        <div class="recipe-meta">
          <div class="meta-item" v-if="recipe.cuisine">
            <span>🍽️</span>
            <span>{{ $t(`cuisines.${recipe.cuisine}`) }}</span>
          </div>
          
          <div class="meta-item" v-if="recipe.difficulty">
            <span>⭐</span>
            <span>{{ $t(`difficulties.${recipe.difficulty}`) }}</span>
          </div>
          
          <div class="meta-item" v-if="recipe.preparationTime || recipe.cookingTime">
            <span>⏱️</span>
            <span>{{ formatCookingTime(recipe.cookingTime || 30) }}</span>
          </div>
          
          <div class="meta-item" v-if="recipe.servings">
            <span>👥</span>
            <span>{{ $t('recipe.servings', { count: recipe.servings || 2 }) }}</span>
          </div>
        </div>
        
        <div class="recipe-tags" v-if="recipe.tags && recipe.tags.length > 0">
          <el-tag 
            v-for="tag in recipe.tags" 
            :key="tag" 
            size="small" 
            class="recipe-tag"
          >
            {{ tag }}
          </el-tag>
        </div>
      </div>
      
      <!-- 菜谱图片 -->
      <div class="recipe-image-container">
        <img 
          :src="recipe.image || '/images/recipe-placeholder.jpg'" 
          :alt="recipe.name" 
          class="recipe-image"
        />
        
        <!-- 视频链接 -->
        <a 
          v-if="recipe.videoUrl" 
          :href="recipe.videoUrl" 
          target="_blank" 
          class="video-link"
        >
          <span>📹</span>
          {{ $t('recipeDetail.watchVideo') }}
        </a>
      </div>
      
      <div class="recipe-details-grid">
        <!-- 营养信息 -->
        <div class="recipe-section nutrition-section" v-if="recipe.nutrition">
          <h2>{{ $t('recipeDetail.nutritionInfo') }}</h2>
          
          <div class="nutrition-grid">
            <div class="nutrition-item">
              <div class="nutrition-value">{{ recipe.nutrition.calories || 0 }}</div>
              <div class="nutrition-label">{{ $t('recipe.calories') }}</div>
            </div>
            
            <div class="nutrition-item">
              <div class="nutrition-value">{{ recipe.nutrition.protein || 0 }}g</div>
              <div class="nutrition-label">{{ $t('recipe.protein') }}</div>
            </div>
            
            <div class="nutrition-item">
              <div class="nutrition-value">{{ recipe.nutrition.fat || 0 }}g</div>
              <div class="nutrition-label">{{ $t('recipe.fat') }}</div>
            </div>
            
            <div class="nutrition-item">
              <div class="nutrition-value">{{ recipe.nutrition.carbs || 0 }}g</div>
              <div class="nutrition-label">{{ $t('recipe.carbs') }}</div>
            </div>
          </div>
        </div>
        
        <!-- 食材列表 -->
        <div class="recipe-section ingredients-section">
          <h2>{{ $t('recipeDetail.ingredients') }}</h2>
          
          <ul class="ingredients-list">
            <li 
              v-for="(ingredient, index) in recipe.stuff" 
              :key="index" 
              class="ingredient-item"
            >
              <span class="ingredient-name">{{ ingredient }}</span>
            </li>
          </ul>
        </div>
        
        <!-- 厨具列表 -->
        <div class="recipe-section cookwares-section" v-if="recipe.tools && recipe.tools.length > 0">
          <h2>{{ $t('recipeDetail.cookware') }}</h2>
          
          <div class="cookwares-list">
            <div 
              v-for="(tool, index) in recipe.tools" 
              :key="index"
              class="cookware-item"
            >
              <span>🍳</span>
              {{ tool }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- 统一的步骤列表 -->
      <div class="recipe-section steps-section">
        <h2>{{ $t('recipeDetail.instructions') }}</h2>
        <div v-if="recipe.steps && recipe.steps.length > 0" class="steps-list">
          <div v-for="(step, index) in recipe.steps" :key="index" class="step-item-unified">
            <p class="step-text">{{ step.text }}</p>
          </div>
        </div>
        <el-empty v-else :description="$t('recipeDetail.noSteps')" />
      </div>
      
      <!-- 相关菜谱 -->
      <div class="recipe-section related-section">
        <h2>{{ $t('recipeDetail.relatedRecipes') }}</h2>
        
        <div v-if="relatedRecipes.length > 0" class="related-recipes-grid">
          <el-row :gutter="20">
            <el-col 
              v-for="relatedRecipe in relatedRecipes" 
              :key="relatedRecipe.id"
              :xs="24" 
              :sm="12" 
              :md="8" 
              :lg="6"
              class="related-recipe-col"
            >
              <recipe-card 
                :recipe="relatedRecipe"
                @favorite-change="onFavoriteChange"
              />
            </el-col>
          </el-row>
        </div>
        <el-empty v-else :description="$t('recipeDetail.noRelatedRecipes')" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import RecipeCard from '../components/RecipeCard.vue';
import { getRecipeById, getRelatedRecipes } from '../api/recipeService';
import { formatCookingTime } from '../utils/helpers';
import { 
  addToFavorites, 
  removeFromFavorites, 
  getFavoriteRecipes, 
  addToHistory 
} from '../api/userService';

const route = useRoute();
const router = useRouter();
const { t } = useI18n();

// 状态变量
const recipe = ref(null);
const relatedRecipes = ref([]);
const loading = ref(true);
const error = ref(false);
const isFavorite = ref(false);

// 监听路由参数变化
watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
      fetchRecipe(newId);
    }
  }
);

// 格式化时间
const formatTime = (preparationTime, cookingTime) => {
  const total = (preparationTime || 0) + (cookingTime || 0);
  return formatCookingTime(total);
};

// 获取菜谱详情
const fetchRecipe = async (id) => {
  loading.value = true;
  error.value = false;
  
  try {
    // 获取菜谱详情
    recipe.value = await getRecipeById(id);
    
    if (recipe.value) {
      // 添加到浏览历史
      await addToHistory(recipe.value);
      
      // 获取相关菜谱
      relatedRecipes.value = await getRelatedRecipes(recipe.value.id, 4);
      
      // 检查是否收藏
      checkIfFavorite();
    } else {
      error.value = true;
    }
  } catch (err) {
    console.error('获取菜谱详情失败:', err);
    error.value = true;
  } finally {
    loading.value = false;
  }
};

// 检查是否已收藏
const checkIfFavorite = async () => {
  try {
    const favorites = await getFavoriteRecipes();
    isFavorite.value = favorites.includes(recipe.value.id);
  } catch (error) {
    console.error('检查收藏状态失败:', error);
  }
};

// 切换收藏状态
const toggleFavorite = async () => {
  try {
    if (isFavorite.value) {
      await removeFromFavorites(recipe.value.id);
    } else {
      await addToFavorites(recipe.value.id);
    }
    
    isFavorite.value = !isFavorite.value;
    
    ElMessage({
      message: isFavorite.value 
        ? t('recipeDetail.addedToFavorites')
        : t('recipeDetail.removedFromFavorites'),
      type: 'success'
    });
  } catch (error) {
    console.error('切换收藏状态失败:', error);
  }
};

// 返回上一页
const goBack = () => {
  router.back();
};

// 组件挂载时加载数据
onMounted(() => {
  const { id } = route.params;
  if (id) {
    fetchRecipe(id);
  } else {
    error.value = true;
    loading.value = false;
  }
});
</script>

<style scoped>
.recipe-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading-container,
.error-container {
  min-height: 70vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.back-navigation {
  margin-bottom: 20px;
}

.recipe-header {
  margin-bottom: 30px;
}

.recipe-title-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.recipe-title {
  font-size: 2.5rem;
  margin: 0;
  color: var(--el-text-color-primary);
}

.recipe-description {
  font-size: 1.1rem;
  color: var(--el-text-color-regular);
  margin-bottom: 15px;
  line-height: 1.6;
}

.recipe-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 15px;
}

.meta-item {
  display: flex;
  align-items: center;
  color: var(--el-text-color-secondary);
}

.meta-item i {
  margin-right: 8px;
}

.recipe-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.recipe-image-container {
  margin-bottom: 30px;
  position: relative;
}

.recipe-image {
  width: 100%;
  max-height: 500px;
  object-fit: cover;
  border-radius: 8px;
}

.video-link {
  position: absolute;
  bottom: 15px;
  right: 15px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px 15px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  text-decoration: none;
  transition: background-color 0.3s;
}

.video-link:hover {
  background: rgba(0, 0, 0, 0.9);
}

.video-link i {
  margin-right: 8px;
}

.recipe-details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

.recipe-section {
  margin-bottom: 30px;
  background-color: var(--el-bg-color);
  border-radius: 8px;
  padding: 20px;
  box-shadow: var(--el-box-shadow-light);
}

.recipe-section h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: var(--el-text-color-primary);
  font-size: 1.5rem;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.nutrition-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  text-align: center;
}

.nutrition-item {
  background-color: var(--el-fill-color-lighter);
  padding: 15px;
  border-radius: 8px;
}

.nutrition-value {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 5px;
  color: var(--el-color-primary);
}

.nutrition-label {
  font-size: 0.9rem;
  color: var(--el-text-color-secondary);
}

.ingredients-list,
.cookwares-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.ingredient-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px dashed var(--el-border-color-lighter);
}

.ingredient-item:last-child {
  border-bottom: none;
}

.optional-ingredient {
  opacity: 0.7;
}

.optional-label {
  font-style: italic;
  color: var(--el-text-color-secondary);
}

.cookware-item {
  padding: 10px 0;
  border-bottom: 1px dashed var(--el-border-color-lighter);
  display: flex;
  align-items: center;
}

.cookware-item:last-child {
  border-bottom: none;
}

.cookware-item i {
  margin-right: 10px;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.step-item {
  display: flex;
  margin-bottom: 20px;
}

.step-number {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--el-color-primary);
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  margin-right: 15px;
}

.step-content {
  font-size: 1rem;
  line-height: 1.6;
}

.step-item-unified {
  margin-bottom: 12px;
}

.step-text {
  font-size: 1rem;
  line-height: 1.7;
  white-space: pre-wrap; /* 保留CSV中的换行 */
}

.related-recipe-col {
  margin-bottom: 20px;
}

.related-recipe {
  cursor: pointer;
  transition: transform 0.3s;
  border-radius: 8px;
  overflow: hidden;
}

.related-recipe:hover {
  transform: translateY(-5px);
}

.related-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.related-name {
  padding: 10px;
  background-color: var(--el-fill-color-lighter);
  font-weight: bold;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.favorite-button {
  font-size: 1.5rem;
  color: #c0c4cc;
  transition: color 0.3s, transform 0.3s;
}

.favorite-button:hover {
  transform: scale(1.1);
}

.favorite-button.is-favorite {
  color: #e6a23c;
}

@media (max-width: 768px) {
  .recipe-details-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .nutrition-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .related-recipes {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .recipe-title {
    font-size: 2rem;
  }
}
</style> 