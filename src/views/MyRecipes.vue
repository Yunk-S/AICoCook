<template>
  <div class="my-recipes">
    <!-- 背景层：紫色光晕 -->
    <div class="hero-background">
      <div class="radial-gradient"></div>
      <div class="purple-glow"></div>
    </div>
    
    <h1 class="page-title">{{ $t('myRecipes.title') }}</h1>
    <p class="page-description">{{ $t('myRecipes.description') }}</p>
    
    <el-tabs v-model="activeTab" class="recipe-tabs">
      <!-- 收藏标签页 -->
      <el-tab-pane :label="$t('myRecipes.favorites')" name="favorites">
        <div v-if="favoritesLoading" class="loading-container">
          <el-skeleton animated :rows="5" />
        </div>
        <el-empty v-else-if="paginatedFavorites.length === 0" :description="$t('myRecipes.noFavorites')">
          <el-button type="primary" @click="goToFoodGallery">{{ $t('myRecipes.browseGallery') }}</el-button>
        </el-empty>
        <div v-else class="recipes-grid">
           <el-row :gutter="20">
            <el-col v-for="item in paginatedFavorites" :key="item.id" :xs="24" :sm="12" :md="8" :lg="6">
              <RecipeCard :recipe="item" />
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>
      
      <!-- 历史标签页 -->
      <el-tab-pane :label="$t('myRecipes.history')" name="history">
        <div v-if="historyLoading" class="loading-container">
          <el-skeleton animated :rows="5" />
        </div>
        <el-empty v-else-if="paginatedHistory.length === 0" :description="$t('myRecipes.noHistory')">
          <el-button type="primary" @click="goToFoodGallery">{{ $t('myRecipes.startBrowsing') }}</el-button>
        </el-empty>
        <div v-else>
          <div class="action-bar">
            <el-button type="danger" plain @click="confirmClearHistory">{{ $t('myRecipes.clearHistory') }}</el-button>
          </div>
          <div class="recipes-grid">
            <el-row :gutter="20">
              <el-col v-for="item in paginatedHistory" :key="item.id" :xs="24" :sm="12" :md="8" :lg="6">
                <RecipeCard :recipe="item" />
              </el-col>
            </el-row>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="totalPages > 1">
      <el-pagination
        background
        layout="prev, pager, next"
        :total="totalItems"
        :page-size="pageSize"
        v-model:current-page="currentPage"
        class="modern-pagination"
      />
    </div>

    <!-- 确认对话框 -->
     <el-dialog 
       v-model="clearHistoryDialogVisible" 
       :title="$t('myRecipes.confirmClearHistory')" 
       width="400px"
       class="custom-confirm-dialog"
       :show-close="true"
       :close-on-click-modal="false"
       :close-on-press-escape="true"
     >
       <span>{{ $t('myRecipes.clearHistoryWarning') }}</span>
       <template #footer>
         <el-button @click="clearHistoryDialogVisible = false">{{ $t('common.cancel') }}</el-button>
         <el-button type="danger" @click="handleClearHistory">{{ $t('common.confirm') }}</el-button>
       </template>
     </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { ElMessage, ElMessageBox } from 'element-plus';
import RecipeCard from '../components/RecipeCard.vue';
import { getFavoriteRecipes, removeFromFavorites, getHistoryRecipes, clearHistory } from '../api/userService';

const router = useRouter();
const { t } = useI18n();

const activeTab = ref('favorites');
const favorites = ref([]);
const history = ref([]);
const favoritesLoading = ref(true);
const historyLoading = ref(true);
const clearHistoryDialogVisible = ref(false);

const currentPage = ref(1);
const pageSize = ref(12);

// --- Computed Properties ---

const paginatedFavorites = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return favorites.value.slice(start, end);
});

const paginatedHistory = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return history.value.slice(start, end);
});

const totalItems = computed(() => {
  return activeTab.value === 'favorites' ? favorites.value.length : history.value.length;
});

const totalPages = computed(() => {
  return Math.ceil(totalItems.value / pageSize.value);
});

// --- Methods ---

const loadData = async () => {
  favoritesLoading.value = true;
  historyLoading.value = true;
  try {
    const favs = await getFavoriteRecipes(true);
    favorites.value = favs.sort((a, b) => new Date(b.addedAt) - new Date(a.addedAt));

    const hist = await getHistoryRecipes(true);
    history.value = hist.sort((a, b) => new Date(b.viewedAt) - new Date(a.viewedAt));
  } catch (error) {
    console.error('Failed to load user recipes:', error);
    ElMessage.error('加载数据失败');
  } finally {
    favoritesLoading.value = false;
    historyLoading.value = false;
  }
};

const goToFoodGallery = () => {
  router.push('/food-gallery');
};

const confirmClearHistory = () => {
  clearHistoryDialogVisible.value = true;
};

const handleClearHistory = async () => {
  try {
    await clearHistory();
    history.value = [];
    ElMessage.success(t('myRecipes.historyCleared'));
  } catch (error) {
    ElMessage.error(t('myRecipes.clearHistoryError'));
  } finally {
    clearHistoryDialogVisible.value = false;
  }
};

watch(activeTab, () => {
  currentPage.value = 1;
});

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.my-recipes {
  padding: 24px;
}
.page-title {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 8px;
  text-align: center;
}
.page-description {
  font-size: 1rem;
  color: var(--el-text-color-secondary);
  margin-bottom: 24px;
  text-align: center;
}
.recipe-tabs {
  min-height: 500px;
}
.recipes-grid {
  margin-top: 24px;
}
.loading-container, .empty-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
.action-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}
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
:root:not(.dark) .my-recipes {
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
</style>

<style>
/* 自定义确认对话框样式 */
.custom-confirm-dialog .el-dialog {
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
.dark .custom-confirm-dialog .el-dialog {
  background: rgba(31, 41, 55, 0.95) !important;
  border: 1px solid rgba(75, 85, 99, 0.3) !important;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    0 2px 8px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
}

/* 对话框头部 */
.custom-confirm-dialog .el-dialog__header {
  padding: 24px 24px 16px 24px !important;
  border-bottom: 1px solid rgba(229, 231, 235, 0.3) !important;
}

.dark .custom-confirm-dialog .el-dialog__header {
  border-bottom: 1px solid rgba(75, 85, 99, 0.3) !important;
}

.custom-confirm-dialog .el-dialog__title {
  font-size: 1.25rem !important;
  font-weight: 600 !important;
  color: var(--el-text-color-primary) !important;
}

/* 对话框内容 */
.custom-confirm-dialog .el-dialog__body {
  padding: 20px 24px !important;
  font-size: 1rem !important;
  line-height: 1.6 !important;
  color: var(--el-text-color-regular) !important;
}

/* 对话框底部按钮区域 */
.custom-confirm-dialog .el-dialog__footer {
  padding: 16px 24px 24px 24px !important;
  border-top: 1px solid rgba(229, 231, 235, 0.3) !important;
  background: transparent !important;
  text-align: right !important;
}

.dark .custom-confirm-dialog .el-dialog__footer {
  border-top: 1px solid rgba(75, 85, 99, 0.3) !important;
}

/* 毛玻璃按钮样式 */
.custom-confirm-dialog .el-button {
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
.custom-confirm-dialog .el-button--default {
  background: rgba(107, 114, 128, 0.1) !important;
  color: var(--el-text-color-regular) !important;
  border-color: rgba(107, 114, 128, 0.2) !important;
}

.custom-confirm-dialog .el-button--default:hover {
  background: rgba(107, 114, 128, 0.2) !important;
  border-color: rgba(107, 114, 128, 0.3) !important;
  transform: translateY(-1px) !important;
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
}

/* 确认按钮 */
.custom-confirm-dialog .el-button--danger {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.9), rgba(220, 38, 38, 0.9)) !important;
  color: white !important;
  border-color: rgba(239, 68, 68, 0.4) !important;
}

.custom-confirm-dialog .el-button--danger:hover {
  background: linear-gradient(135deg, rgba(239, 68, 68, 1), rgba(220, 38, 38, 1)) !important;
  border-color: rgba(239, 68, 68, 0.6) !important;
  transform: translateY(-1px) !important;
  box-shadow: 
    0 4px 12px rgba(239, 68, 68, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
}

/* 深色模式下的按钮 */
.dark .custom-confirm-dialog .el-button--default {
  background: rgba(75, 85, 99, 0.3) !important;
  border-color: rgba(75, 85, 99, 0.4) !important;
}

.dark .custom-confirm-dialog .el-button--default:hover {
  background: rgba(75, 85, 99, 0.5) !important;
  border-color: rgba(75, 85, 99, 0.6) !important;
}

/* 关闭按钮 */
.custom-confirm-dialog .el-dialog__headerbtn {
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

.custom-confirm-dialog .el-dialog__headerbtn:hover {
  background: rgba(107, 114, 128, 0.2) !important;
  border-color: rgba(107, 114, 128, 0.3) !important;
  transform: scale(1.05) !important;
}

.custom-confirm-dialog .el-dialog__close {
  font-size: 16px !important;
  color: var(--el-text-color-regular) !important;
}

/* 暗色模式下的分页样式 */
@media (prefers-color-scheme: dark) {
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
  
  .modern-pagination :deep(.btn-prev:hover),
  .modern-pagination :deep(.btn-next:hover) {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.4), rgba(118, 75, 162, 0.4)) !important;
    color: #ffffff !important;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .custom-confirm-dialog .el-dialog {
    margin: 20px !important;
    width: calc(100% - 40px) !important;
  }
  
  .custom-confirm-dialog .el-dialog__footer {
    flex-direction: column !important;
  }
  
  .custom-confirm-dialog .el-button {
    margin: 6px 0 !important;
    width: 100% !important;
  }
}
</style> 