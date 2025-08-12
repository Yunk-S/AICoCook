<template>
  <el-card :body-style="{ padding: '0px' }" class="recipe-card modern-recipe-card" shadow="hover" @click="handleCardClick">
    <div class="recipe-image">
      <img :src="recipe.image || '/images/recipe-placeholder.jpg'" :alt="recipe.name" />
      <div class="image-overlay"></div>
      <div class="recipe-actions">
        <el-button 
          link
          size="small" 
          class="favorite-btn modern-favorite-btn"
          @click.stop="toggleFavorite"
          :class="{ 'is-favorited': isFavorite }"
        >
          <span v-if="isFavorite">❤️</span>
          <span v-else>🤍</span>
        </el-button>
      </div>
    </div>
    
    <div class="recipe-content">
      <h3 class="recipe-name" :title="recipe.name">{{ recipe.name }}</h3>
      
      <div class="recipe-meta">
        <div class="recipe-meta-item" v-if="recipe.videoUrl">
          <a :href="recipe.videoUrl" target="_blank" class="video-link" @click.stop>
            <span>📹</span>
            {{ $t('recipeDetail.watchVideo') }}
          </a>
        </div>
        <div class="recipe-difficulty" :class="difficultyClass">
          {{ $t(`difficulties.${recipe.difficulty || 'medium'}`) }}
        </div>
      </div>
    </div>
    
    <!-- 插槽，用于显示匹配信息 -->
    <div class="match-info-slot">
      <slot name="match-info"></slot>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { isFavorite as checkIsFavorite, addToFavorites, removeFromFavorites } from '../api/userService';
import { useI18n } from 'vue-i18n';
import { formatDate } from '../utils/helpers';

const { t } = useI18n();
const router = useRouter();

const props = defineProps({
  recipe: {
    type: Object,
    required: true,
    default: () => ({
      id: '',
      name: '加载中...',
      cover: '',
      tags: [],
      difficulty: '',
      rating: 0,
      author: '匿名',
      publishTime: new Date().toISOString(),
    })
  }
});

const emit = defineEmits(['click', 'favorite-change']);

const isFavorite = ref(false);

const defaultCover = '/images/default_recipe_cover.jpg';
const coverImage = computed(() => {
  if (!props.recipe) {
    return defaultCover;
  }
  return props.recipe.cover || defaultCover;
});

const difficultyClass = computed(() => {
  const difficulty = props.recipe.difficulty || 'medium';
  return {
    'difficulty-easy': difficulty === 'easy',
    'difficulty-medium': difficulty === 'medium',
    'difficulty-hard': difficulty === 'hard',
  };
});

// 检查菜谱是否已收藏
const checkFavoriteStatus = async () => {
  try {
    if (props.recipe.id) {
        isFavorite.value = await checkIsFavorite(props.recipe.id);
    }
  } catch (error) {
    console.error('检查收藏状态失败:', error);
  }
};

// 切换收藏状态
const toggleFavorite = async () => {
  try {
    if (isFavorite.value) {
      await removeFromFavorites(props.recipe.id);
      isFavorite.value = false;
    } else {
      await addToFavorites(props.recipe);
      isFavorite.value = true;
    }
    
    // 通知父组件收藏状态变化
    emit('favorite-change', {
      recipe: props.recipe,
      isFavorite: isFavorite.value
    });
  } catch (error) {
    console.error('切换收藏状态失败:', error);
  }
};

// 处理卡片点击，自己跳转
const handleCardClick = () => {
  console.log('[Debug] RecipeCard clicked. Recipe data:', props.recipe);
  
  if (props.recipe && props.recipe.id) {
    const navigationPath = `/recipe/${props.recipe.id}`;
    console.log(`[Debug] Navigating to: ${navigationPath}`);
    
    try {
      emit('click'); // 依然通知父组件
      router.push(navigationPath);
      console.log('[Debug] router.push command issued successfully.');
    } catch (e) {
      console.error('[Debug] Error during router.push:', e);
    }
  } else {
    console.error('[Debug] Navigation failed: Recipe ID is missing or invalid.', props.recipe);
  }
};

onMounted(() => {
  checkFavoriteStatus();
});

</script>

<style scoped>
/* 现代化食谱卡片样式 */
.modern-recipe-card {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.08),
    0 4px 16px rgba(0, 0, 0, 0.04);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.modern-recipe-card:hover {
  transform: translateY(-12px) scale(1.02);
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.15),
    0 8px 24px rgba(0, 0, 0, 0.08);
  border-color: rgba(102, 126, 234, 0.3);
}

.recipe-card {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  background-color: var(--el-bg-color);
  box-shadow: var(--el-box-shadow-light);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.recipe-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--el-box-shadow);
}

.recipe-image {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.recipe-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.modern-recipe-card:hover .recipe-image img {
  transform: scale(1.08);
  filter: brightness(1.1) saturate(1.2);
}

.recipe-card:hover .recipe-image img {
  transform: scale(1.05);
}

/* 图片覆盖层 */
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

.modern-recipe-card:hover .image-overlay {
  opacity: 1;
}

.recipe-content {
  padding: 15px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.recipe-name {
  margin: 0 0 10px 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
  line-height: 1.2;
  height: 2.4em; /* 设置一个固定高度，允许最多显示两行 */
  white-space: normal; /* 允许换行 */
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2; /* 限制最多显示两行 */
  -webkit-box-orient: vertical;
}

.recipe-emojis {
  margin-bottom: 10px;
}

.emoji {
  margin-right: 5px;
  font-size: 1.2rem;
}

.recipe-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--el-text-color-secondary);
  font-size: 0.9rem;
  margin-top: auto;
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
  color: inherit;
}

.recipe-difficulty {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
  color: #fff;
}

.difficulty-easy {
  background-color: rgba(103, 194, 58, 0.8);
}

.difficulty-medium {
  background-color: rgba(230, 162, 60, 0.8);
}

.difficulty-hard {
  background-color: rgba(245, 108, 108, 0.8);
}

.recipe-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 10;
}

.modern-favorite-btn {
  font-size: 1.8rem;
  padding: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modern-favorite-btn:hover {
  background: rgba(255, 255, 255, 1) !important;
  transform: scale(1.15) rotate(10deg);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.modern-favorite-btn.is-favorited {
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e) !important;
  color: white !important;
  animation: heartbeat 1.5s ease-in-out infinite;
}

@keyframes heartbeat {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.favorite-btn {
  font-size: 1.5rem;
  padding: 5px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.7);
  transition: all 0.2s;
}

.favorite-btn:hover {
  background-color: rgba(255, 255, 255, 0.9);
  transform: scale(1.1);
}

.favorite-btn.is-favorited {
  color: #ff4500;
}
</style> 