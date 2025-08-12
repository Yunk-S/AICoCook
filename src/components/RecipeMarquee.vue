<template>
  <div class="recipe-marquee-section">
    <div class="marquee-container">
      <!-- 标题区域 -->
      <div class="marquee-header">
        <h2 class="marquee-title">{{ title }}</h2>
        <p class="marquee-subtitle">{{ subtitle }}</p>
      </div>
      
      <!-- 滚动容器 -->
      <div class="marquee-wrapper" @mouseenter="pauseAnimation" @mouseleave="resumeAnimation">
        <!-- 左侧渐变遮罩 -->
        <div class="gradient-mask gradient-left"></div>
        
        <!-- 滚动内容 -->
        <div 
          class="marquee-content" 
          :style="{ 
            '--duration': `${duration}s`,
            '--gap': gap,
            animationPlayState: isPaused ? 'paused' : 'running'
          }"
        >
          <!-- 原始卡片组 -->
          <div class="marquee-group">
            <div 
              v-for="recipe in displayRecipes" 
              :key="`original-${recipe.id}`"
              class="marquee-item"
            >
              <div class="recipe-marquee-card" @click="handleRecipeClick(recipe)">
                <div class="card-image">
                  <img 
                    :src="recipe.image || '/images/recipe-placeholder.jpg'" 
                    :alt="recipe.name"
                    @error="handleImageError"
                  />
                  <div class="image-overlay"></div>
                  <div class="card-actions">
                    <button 
                      class="favorite-btn"
                      @click.stop="toggleFavorite(recipe)"
                      :class="{ 'is-favorited': isFavoriteRecipe(recipe.id) }"
                    >
                      <span v-if="isFavoriteRecipe(recipe.id)">❤️</span>
                      <span v-else>🤍</span>
                    </button>
                  </div>
                </div>
                
                <div class="card-content">
                  <h3 class="card-title">{{ recipe.name }}</h3>
                  <div class="card-meta">
                    <div class="recipe-meta-item" v-if="recipe.videoUrl">
                      <a :href="recipe.videoUrl" target="_blank" class="video-link" @click.stop>
                        <span>📹</span>
                        {{ $t('recipeDetail.watchVideo') }}
                      </a>
                    </div>
                    <div class="recipe-difficulty" :class="getDifficultyClass(recipe.difficulty)">
                      {{ $t(`difficulties.${recipe.difficulty || 'medium'}`) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 重复的卡片组，用于无限滚动 -->
          <div class="marquee-group">
            <div 
              v-for="recipe in displayRecipes" 
              :key="`duplicate-${recipe.id}`"
              class="marquee-item"
            >
              <div class="recipe-marquee-card" @click="handleRecipeClick(recipe)">
                <div class="card-image">
                  <img 
                    :src="recipe.image || '/images/recipe-placeholder.jpg'" 
                    :alt="recipe.name"
                    @error="handleImageError"
                  />
                  <div class="image-overlay"></div>
                  <div class="card-actions">
                    <button 
                      class="favorite-btn"
                      @click.stop="toggleFavorite(recipe)"
                      :class="{ 'is-favorited': isFavoriteRecipe(recipe.id) }"
                    >
                      <span v-if="isFavoriteRecipe(recipe.id)">❤️</span>
                      <span v-else>🤍</span>
                    </button>
                  </div>
                </div>
                
                <div class="card-content">
                  <h3 class="card-title">{{ recipe.name }}</h3>
                  <div class="card-meta">
                    <div class="recipe-meta-item" v-if="recipe.videoUrl">
                      <a :href="recipe.videoUrl" target="_blank" class="video-link" @click.stop>
                        <span>📹</span>
                        {{ $t('recipeDetail.watchVideo') }}
                      </a>
                    </div>
                    <div class="recipe-difficulty" :class="getDifficultyClass(recipe.difficulty)">
                      {{ $t(`difficulties.${recipe.difficulty || 'medium'}`) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 右侧渐变遮罩 -->
        <div class="gradient-mask gradient-right"></div>
      </div>
      
      <!-- 查看更多按钮 -->
      <div class="view-more-container">
        <el-button type="primary" plain @click="handleViewMore">
          {{ $t('home.viewMore') }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import { 
  isFavorite as checkIsFavorite, 
  addToFavorites, 
  removeFromFavorites 
} from '../api/userService';
import { getAllRecipesService } from '../api/recipeService';

const router = useRouter();
const { t } = useI18n();

const props = defineProps({
  title: {
    type: String,
    default: '随机推荐'
  },
  subtitle: {
    type: String,
    default: '发现新的灵感，每天不重样'
  },
  duration: {
    type: Number,
    default: 40
  },
  gap: {
    type: String,
    default: '1rem'
  },
  recipeCount: {
    type: Number,
    default: 16
  }
});

const emit = defineEmits(['recipe-click', 'favorite-change', 'view-more']);

const recipes = ref([]);
const favoriteRecipes = ref(new Set());
const isPaused = ref(false);

// 显示的菜谱数据
const displayRecipes = computed(() => {
  return recipes.value.slice(0, props.recipeCount);
});

// 加载菜谱数据
const loadRecipes = async () => {
  try {
    const allRecipes = await getAllRecipesService();
    // 随机打乱并获取指定数量的菜谱
    const shuffled = allRecipes.sort(() => 0.5 - Math.random());
    recipes.value = shuffled.slice(0, props.recipeCount);
  } catch (error) {
    console.error('加载菜谱失败:', error);
    recipes.value = [];
  }
};

// 检查是否为收藏菜谱
const isFavoriteRecipe = (recipeId) => {
  return favoriteRecipes.value.has(recipeId);
};

// 获取难度等级样式类
const getDifficultyClass = (difficulty) => {
  const level = difficulty || 'medium';
  return `difficulty-${level}`;
};

// 处理菜谱点击
const handleRecipeClick = (recipe) => {
  emit('recipe-click', recipe);
  router.push(`/recipe/${recipe.id}`);
};

// 切换收藏状态
const toggleFavorite = async (recipe) => {
  try {
    const isFavorited = favoriteRecipes.value.has(recipe.id);
    
    if (isFavorited) {
      await removeFromFavorites(recipe.id);
      favoriteRecipes.value.delete(recipe.id);
      ElMessage.success(`已取消收藏 「${recipe.name}」`);
    } else {
      await addToFavorites(recipe);
      favoriteRecipes.value.add(recipe.id);
      ElMessage.success(`已收藏 「${recipe.name}」`);
    }
    
    emit('favorite-change', {
      recipe,
      isFavorite: !isFavorited
    });
  } catch (error) {
    console.error('切换收藏状态失败:', error);
    ElMessage.error('操作失败，请重试');
  }
};

// 加载收藏状态
const loadFavoriteStatus = async () => {
  try {
    for (const recipe of recipes.value) {
      const isFavorited = await checkIsFavorite(recipe.id);
      if (isFavorited) {
        favoriteRecipes.value.add(recipe.id);
      }
    }
  } catch (error) {
    console.error('加载收藏状态失败:', error);
  }
};

// 暂停动画
const pauseAnimation = () => {
  isPaused.value = true;
};

// 恢复动画
const resumeAnimation = () => {
  isPaused.value = false;
};

// 处理图片加载错误
const handleImageError = (event) => {
  event.target.src = '/images/recipe-placeholder.jpg';
};

// 处理查看更多
const handleViewMore = () => {
  emit('view-more');
};

onMounted(async () => {
  await loadRecipes();
  await loadFavoriteStatus();
});
</script>

<style scoped>
.recipe-marquee-section {
  background: transparent;
  color: var(--el-text-color-primary);
  padding: 48px 0;
  position: relative;
  overflow: hidden;
}

@media (min-width: 640px) {
  .recipe-marquee-section {
    padding: 96px 0;
  }
}

@media (min-width: 768px) {
  .recipe-marquee-section {
    padding: 128px 0;
  }
}

.marquee-container {
  max-width: 1280px;
  margin: 0 auto;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@media (min-width: 640px) {
  .marquee-container {
    gap: 64px;
  }
}

.marquee-header {
  padding: 0 20px;
}

.marquee-title {
  font-size: 1.875rem;
  font-weight: 600;
  line-height: 1.2;
  margin: 0 0 16px 0;
  max-width: 720px;
  margin-left: auto;
  margin-right: auto;
}

@media (min-width: 640px) {
  .marquee-title {
    font-size: 3rem;
  }
}

.marquee-subtitle {
  font-size: 1rem;
  color: #94a3b8;
  font-weight: 500;
  margin: 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

@media (min-width: 640px) {
  .marquee-subtitle {
    font-size: 1.25rem;
  }
}

.marquee-wrapper {
  position: relative;
  overflow: hidden;
  width: 100%;
}

.gradient-mask {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 120px;
  z-index: 10;
  pointer-events: none;
  display: block;
}

@media (min-width: 640px) {
  .gradient-mask {
    width: 150px;
  }
}

@media (min-width: 1024px) {
  .gradient-mask {
    width: 200px;
  }
}

.gradient-left {
  left: 0;
  background: linear-gradient(to right, var(--el-bg-color-page), transparent);
}

.gradient-right {
  right: 0;
  background: linear-gradient(to left, var(--el-bg-color-page), transparent);
}

.marquee-content {
  display: flex;
  gap: var(--gap);
  animation: marquee var(--duration) linear infinite;
  width: max-content;
}

.marquee-content:hover {
  animation-play-state: paused;
}

@keyframes marquee {
  from {
    transform: translateX(0%);
  }
  to {
    transform: translateX(calc(-50% - var(--gap) / 2));
  }
}

.marquee-group {
  display: flex;
  gap: var(--gap);
}

.marquee-item {
  flex-shrink: 0;
  width: 280px;
}

.recipe-marquee-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--el-box-shadow-light);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  height: 320px;
  display: flex;
  flex-direction: column;
}

.recipe-marquee-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.card-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.recipe-marquee-card:hover .card-image img {
  transform: scale(1.1);
  filter: brightness(1.1) saturate(1.2);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.1) 0%,
    rgba(118, 75, 162, 0.1) 100%
  );
  opacity: 0;
  transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.recipe-marquee-card:hover .image-overlay {
  opacity: 1;
}

.card-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 5;
}

.favorite-btn {
  font-size: 1.5rem;
  padding: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.favorite-btn:hover {
  background: rgba(255, 255, 255, 1);
  transform: scale(1.1) rotate(10deg);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.favorite-btn.is-favorited {
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  color: white;
  animation: heartbeat 1.5s ease-in-out infinite;
}

@keyframes heartbeat {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.card-content {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.card-title {
  color: var(--el-text-color-primary);
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 12px 0;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
}

.recipe-difficulty {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #fff;
}

.difficulty-easy {
  background-color: rgba(34, 197, 94, 0.8);
}

.difficulty-medium {
  background-color: rgba(251, 146, 60, 0.8);
}

.difficulty-hard {
  background-color: rgba(239, 68, 68, 0.8);
}

.recipe-meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.video-link {
  display: flex;
  align-items: center;
  gap: 5px;
  text-decoration: none;
  color: var(--el-text-color-secondary);
  font-size: 0.8rem;
}

.video-link:hover {
  color: var(--el-color-primary);
}

.view-more-container {
  text-align: center;
  margin-top: 40px;
  padding: 0 20px;
}

.view-more-container .el-button {
  color: #ffffff !important;
  min-width: 120px;
}

.view-more-container .el-button:hover {
  color: #ffffff !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .marquee-item {
    width: 240px;
  }
  
  .recipe-marquee-card {
    height: 280px;
  }
  
  .card-image {
    height: 160px;
  }
}

/* 深色模式优化 */
@media (prefers-color-scheme: dark) {
  .recipe-marquee-card {
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color-light);
  }
}
</style>