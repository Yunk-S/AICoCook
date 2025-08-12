<template>
  <div class="ai-recommend-page">
    <!-- 背景层：紫色光晕 -->
    <div class="hero-background">
      <div class="radial-gradient"></div>
      <div class="purple-glow"></div>
    </div>
    
    <div class="main-row">
      <div class="health-col">
        <div class="health-form-container">
          <div class="health-header">
            <h2>📊 {{ t('aiRecommend.healthData') }}</h2>
          </div>
          
          <el-form :model="healthForm" label-position="top" class="health-form">
            <!-- 身体数据 -->
            <h3>🏃‍♂️ {{ t('aiRecommend.physicalData') }}</h3>
            
            <!-- 第一行：身高和体重 -->
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item :label="t('aiRecommend.height')">
                  <el-input-number 
                    v-model="healthForm.height" 
                    :min="100" 
                    :max="220" 
                    :step="1" 
                    style="width: 100%"
                    size="small">
                  </el-input-number>
                  <span class="unit">cm</span>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item :label="t('aiRecommend.weight')">
                  <el-input-number 
                    v-model="healthForm.weight" 
                    :min="30" 
                    :max="200" 
                    :step="1" 
                    style="width: 100%"
                    size="small">
                  </el-input-number>
                  <span class="unit">kg</span>
                </el-form-item>
              </el-col>
            </el-row>
            
            <!-- 第二行：年龄和性别 -->
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item :label="t('aiRecommend.age')">
                  <el-input-number 
                    v-model="healthForm.age" 
                    :min="1" 
                    :max="120" 
                    :step="1" 
                    style="width: 100%"
                    size="small">
                  </el-input-number>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item :label="t('aiRecommend.gender')">
                  <el-radio-group v-model="healthForm.gender" size="small">
                    <el-radio value="male">{{ t('aiRecommend.male') }}</el-radio>
                    <el-radio value="female">{{ t('aiRecommend.female') }}</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
            </el-row>
            
            <!-- 活动水平 -->
            <el-form-item :label="t('aiRecommend.activityLevel')">
              <el-select v-model="healthForm.activityLevel" style="width: 100%;" size="small" popper-class="ai-recommend-select-popper">
                <el-option :label="t('aiRecommend.activityLevels.sedentary')" value="sedentary"></el-option>
                <el-option :label="t('aiRecommend.activityLevels.lightlyActive')" value="lightly_active"></el-option>
                <el-option :label="t('aiRecommend.activityLevels.moderatelyActive')" value="moderately_active"></el-option>
                <el-option :label="t('aiRecommend.activityLevels.veryActive')" value="very_active"></el-option>
                <el-option :label="t('aiRecommend.activityLevels.extraActive')" value="extra_active"></el-option>
              </el-select>
            </el-form-item>
            
            <!-- 健康摘要 -->
            <div class="health-summary" v-if="bmi > 0">
              <h3>📈 {{ t('aiRecommend.healthSummary.title') }}</h3>
              <div class="summary-item">
                <span>{{ t('aiRecommend.healthSummary.bmi') }}: </span>
                <strong>{{ bmi.toFixed(1) }}</strong>
                <el-tag :type="bmiStatusTagType(bmiStatus)" effect="light" size="small" class="bmi-status">
                  {{ t(`aiRecommend.healthSummary.status.${bmiStatus}`) }}
                </el-tag>
              </div>
              <div class="summary-item">
                <span>{{ t('aiRecommend.healthSummary.dailyCalories') }}: </span>
                <strong>{{ dailyCalories.toFixed(0) }} {{ t('aiRecommend.healthSummary.calorieUnit') }}</strong>
              </div>
              <div class="advice-box">
                <p class="advice-text">{{ t(dietaryAdvice) }}</p>
              </div>
            </div>
            
            <!-- 饮食偏好 -->
            <h3>🍽️ {{ t('aiRecommend.dietaryPreferences') }}</h3>
            
            <!-- 偏好和避免的食材并排显示 -->
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item :label="t('aiRecommend.preferredIngredients')">
                  <el-select 
                    v-model="preferencesForm.favoriteIngredients" 
                    multiple 
                    filterable
                    allow-create
                    default-first-option
                    :placeholder="t('aiRecommend.selectIngredients')"
                    style="width: 100%;"
                    size="small"
                    popper-class="ai-recommend-select-popper">
                    <el-option 
                      v-for="ingredient in allIngredients" 
                      :key="ingredient.id" 
                      :label="$i18n.locale === 'en' ? ingredient.name_en : ingredient.name" 
                      :value="ingredient.id">
                    </el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item :label="t('aiRecommend.avoidedIngredients')">
                  <el-select 
                    v-model="preferencesForm.avoidedIngredients" 
                    multiple 
                    filterable
                    allow-create
                    default-first-option
                    :placeholder="t('aiRecommend.selectIngredients')"
                    style="width: 100%;"
                    size="small"
                    popper-class="ai-recommend-select-popper">
                    <el-option 
                      v-for="ingredient in allIngredients" 
                      :key="ingredient.id" 
                      :label="$i18n.locale === 'en' ? ingredient.name_en : ingredient.name" 
                      :value="ingredient.id">
                    </el-option>
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            
            <!-- 饮食限制 -->
            <el-form-item :label="t('aiRecommend.dietaryRestrictions')">
              <el-checkbox-group v-model="preferencesForm.restrictions" class="dietary-restrictions">
                <el-checkbox value="vegetarian" size="small">{{ t('aiRecommend.restrictions.vegetarian') }}</el-checkbox>
                <el-checkbox value="vegan" size="small">{{ t('aiRecommend.restrictions.vegan') }}</el-checkbox>
                <el-checkbox value="low_sugar" size="small">{{ t('aiRecommend.restrictions.lowCarb') }}</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-button type="primary" @click="generateRecommendation" :loading="loading" style="width: 100%;" size="default">
              {{ t('aiRecommend.generateRecommendations') }}
            </el-button>
          </el-form>
        </div>
      </div>
      
      <div class="recommend-col">
        <div class="recommendation-container">
          <div class="recommend-header">
            <h2 class="section-title">{{ t('aiRecommend.recommendedForYou') }}</h2>
          </div>
          <div class="recommend-content">
          
          <el-skeleton v-if="loading" :rows="5" animated />
          
          <template v-else-if="recommendedRecipes.length > 0">
            <p class="recommendation-intro">
              {{ t('aiRecommend.recommendationBasis', { bmiValue: bmi.toFixed(1), bmiStatus: t(`aiRecommend.bmiStatus.${bmiStatus}`), calories: dailyCalories.toFixed(0) }) }}
              <span v-if="bmiStatus === 'underweight'">{{ t('aiRecommend.underweightAdvice') }}</span>
              <span v-else-if="bmiStatus === 'normal'">{{ t('aiRecommend.normalWeightAdvice') }}</span>
              <span v-else>{{ t('aiRecommend.overweightAdvice') }}</span>
            </p>
            
            <el-row :gutter="16">
              <el-col v-for="recipe in recommendedRecipes" 
                     :key="recipe.id" 
                     :xs="24" 
                     :sm="12" 
                     :md="12" 
                     :lg="8" 
                     :xl="6"
                     class="recipe-col">
                <recipe-card 
                  :recipe="recipe" 
                  @click="viewRecipeDetail(recipe.id)"
                  @favorite-change="onFavoriteChange"
                />
              </el-col>
            </el-row>
          </template>
          
          <el-empty v-else-if="hasGenerated" :description="t('aiRecommend.noRecommendationsFound')">
            <el-button @click="generateRecommendation">{{ t('aiRecommend.tryAgain') }}</el-button>
          </el-empty>
          
          <div v-else class="recommendation-placeholder">
            <el-empty :description="t('aiRecommend.enterDataForRecommendations')">
              <span class="placeholder-icon">📊</span>
            </el-empty>
          </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';

import RecipeCard from '../components/RecipeCard.vue';
import { calculateBMI, getBMIStatus, calculateDailyCalories } from '../utils/helpers';
// 注意：不再使用后端API，使用纯前端智能推荐算法
import { getUserHealthData, saveUserHealthData, getUserPreferences, saveUserPreferences } from '../api/userService';
import { getAllIngredients, getAllRecipes } from '../api/recipeService';

const router = useRouter();
const { t } = useI18n();
const loading = ref(false);
const hasGenerated = ref(false);
const allIngredients = ref([]);

const healthForm = ref({
  height: 170,
  weight: 65,
  age: 30,
  gender: 'male',
  activityLevel: 'moderately_active'
});

const preferencesForm = ref({
  cuisines: [],
  favoriteIngredients: [],
  avoidedIngredients: [],
  restrictions: []
});

const recommendedRecipes = ref([]);

const bmi = computed(() => {
  return calculateBMI(healthForm.value.weight, healthForm.value.height);
});

const bmiStatus = computed(() => {
  return getBMIStatus(bmi.value);
});

const dailyCalories = computed(() => {
  const { weight, height, age, gender, activityLevel } = healthForm.value;
  return calculateDailyCalories(weight, height, age, gender, activityLevel);
});

// FIXED: Helper function is now defined inside the component
const getDietaryAdviceByBMI = (status) => {
  switch(status) {
    case 'underweight': return 'aiRecommend.dietaryAdvice.underweight';
    case 'normal': return 'aiRecommend.dietaryAdvice.normal';
    case 'overweight': return 'aiRecommend.dietaryAdvice.overweight';
    case 'obese': return 'aiRecommend.dietaryAdvice.obese';
    default: return 'aiRecommend.dietaryAdvice.default';
  }
};

const dietaryAdvice = computed(() => {
  return getDietaryAdviceByBMI(bmiStatus.value);
});

const bmiStatusTagType = (status) => {
  switch (status) {
    case 'underweight': return 'info';
    case 'normal': return 'success';
    case 'overweight': return 'warning';
    case 'obese': return 'danger';
    default: return 'info';
  }
};



// 智能推荐函数 - 改进的推荐算法
const getFallbackRecommendations = async (preferences) => {
  try {
    console.log('开始获取智能推荐，偏好设置:', preferences);
    
    // 获取所有菜谱数据
    const allRecipes = await getAllRecipes();
    console.log('获取到菜谱数据:', allRecipes?.length || 0, '条');
    
    if (!allRecipes || allRecipes.length === 0) {
      console.warn('没有菜谱数据');
      return [];
    }

    let filteredRecipes = [...allRecipes];
    console.log('初始菜谱数量:', filteredRecipes.length);

    // 标准化食材数据 - 处理不同的数据格式
    const normalizeIngredients = (stuff) => {
      if (!stuff) return [];
      if (Array.isArray(stuff)) {
        return stuff.flatMap(item => 
          typeof item === 'string' ? item.split(/[、，,]/) : [item]
        ).map(item => item.trim()).filter(Boolean);
      }
      if (typeof stuff === 'string') {
        return stuff.split(/[、，,]/).map(item => item.trim()).filter(Boolean);
      }
      return [];
    };

    // 基于偏好食材进行过滤（如果有偏好食材，优先推荐包含这些食材的菜谱）
    if (preferences.favoriteIngredients && preferences.favoriteIngredients.length > 0) {
      console.log('应用偏好食材过滤:', preferences.favoriteIngredients);
      const favoriteSet = new Set(preferences.favoriteIngredients.map(ing => ing.toLowerCase()));
      
      const matchedRecipes = filteredRecipes.filter(recipe => {
        const ingredients = normalizeIngredients(recipe.stuff);
        return ingredients.some(ingredient => 
          favoriteSet.has(ingredient.toLowerCase()) || 
          Array.from(favoriteSet).some(fav => ingredient.toLowerCase().includes(fav))
        );
      });
      
      if (matchedRecipes.length > 0) {
        filteredRecipes = matchedRecipes;
        console.log('偏好食材过滤后菜谱数量:', filteredRecipes.length);
      }
    }

    // 排除避免的食材
    if (preferences.avoidedIngredients && preferences.avoidedIngredients.length > 0) {
      console.log('排除避免的食材:', preferences.avoidedIngredients);
      const avoidedSet = new Set(preferences.avoidedIngredients.map(ing => ing.toLowerCase()));
      
      const beforeCount = filteredRecipes.length;
      filteredRecipes = filteredRecipes.filter(recipe => {
        const ingredients = normalizeIngredients(recipe.stuff);
        return !ingredients.some(ingredient => 
          avoidedSet.has(ingredient.toLowerCase()) || 
          Array.from(avoidedSet).some(avoid => ingredient.toLowerCase().includes(avoid))
        );
      });
      console.log(`排除避免食材后菜谱数量: ${beforeCount} -> ${filteredRecipes.length}`);
    }

    // 应用饮食限制 - 改进的识别逻辑
    if (preferences.restrictions && preferences.restrictions.length > 0) {
      console.log('应用饮食限制:', preferences.restrictions);
      
      if (preferences.restrictions.includes('vegetarian')) {
        // 素食主义 - 排除所有肉类和海鲜
        const meatKeywords = [
          // 常见肉类
          '肉', '牛肉', '猪肉', '鸡肉', '羊肉', '鸭肉', '鹅肉',
          // 肉制品
          '腊肠', '香肠', '培根', '火腿', '肉松', '肉丸', '肉饼',
          // 海鲜类
          '鱼', '虾', '蟹', '贝', '蛤', '蚌', '鱿鱼', '章鱼', '海参',
          // 动物内脏
          '肝', '肾', '心', '肺', '肚', '肠', '血',
          // 其他动物产品
          '鸡翅', '鸡腿', '排骨', '牛腩', '猪蹄'
        ];
        
        const beforeCount = filteredRecipes.length;
        filteredRecipes = filteredRecipes.filter(recipe => {
          const ingredients = normalizeIngredients(recipe.stuff);
          const recipeName = recipe.name || '';
          
          // 检查食材和菜名
          const hasMeat = ingredients.some(ingredient => 
            meatKeywords.some(meat => ingredient.includes(meat))
          ) || meatKeywords.some(meat => recipeName.includes(meat));
          
          return !hasMeat;
        });
        console.log(`素食过滤后菜谱数量: ${beforeCount} -> ${filteredRecipes.length}`);
      }
      
      if (preferences.restrictions.includes('vegan')) {
        // 纯素食 - 排除所有动物产品
        const animalProducts = [
          // 肉类（已在素食中排除）
          '肉', '牛', '猪', '鸡', '羊', '鸭', '鹅', '鱼', '虾', '蟹',
          // 蛋类
          '蛋', '鸡蛋', '鸭蛋', '鹌鹑蛋',
          // 奶制品
          '奶', '牛奶', '酸奶', '奶酪', '芝士', '黄油', '奶油', '乳',
          // 蜂蜜
          '蜜', '蜂蜜',
          // 其他动物产品
          '明胶', '鱼胶', '燕窝'
        ];
        
        const beforeCount = filteredRecipes.length;
        filteredRecipes = filteredRecipes.filter(recipe => {
          const ingredients = normalizeIngredients(recipe.stuff);
          const recipeName = recipe.name || '';
          
          const hasAnimalProducts = ingredients.some(ingredient => 
            animalProducts.some(animal => ingredient.includes(animal))
          ) || animalProducts.some(animal => recipeName.includes(animal));
          
          return !hasAnimalProducts;
        });
        console.log(`纯素食过滤后菜谱数量: ${beforeCount} -> ${filteredRecipes.length}`);
      }
      
                   
      if (preferences.restrictions.includes('low_sugar')) {
        // 低糖/低碳水 - 排除高糖高碳水食材
        const highCarbIngredients = [
          '糖', '蜂蜜', '红糖', '白糖', '冰糖',
          '米饭', '面条', '面包', '土豆', '红薯',
          '蛋糕', '甜品', '糖果'
        ];
        
        filteredRecipes = filteredRecipes.filter(recipe => {
          const ingredients = normalizeIngredients(recipe.stuff);
          const recipeName = recipe.name || '';
          
          const hasHighCarb = ingredients.some(ingredient => 
            highCarbIngredients.some(carb => ingredient.includes(carb))
          ) || highCarbIngredients.some(carb => recipeName.includes(carb));
          
          return !hasHighCarb;
        });
      }
    }

    // 如果过滤后菜谱太少，放宽限制
    if (filteredRecipes.length < 3) {
      console.log('过滤后菜谱太少，使用默认推荐');
      // 返回一些健康的热门菜谱
      filteredRecipes = allRecipes.filter(recipe => {
        const recipeName = recipe.name || '';
        return recipeName.includes('蔬菜') || recipeName.includes('汤') || 
               recipeName.includes('沙拉') || recipeName.includes('清蒸');
      }).slice(0, 12);
      
      if (filteredRecipes.length === 0) {
        filteredRecipes = allRecipes.slice(0, 12);
      }
    }

    // 随机选择并限制数量
    const shuffled = filteredRecipes.sort(() => 0.5 - Math.random());
    const result = shuffled.slice(0, 12);
    
    console.log('最终推荐菜谱数量:', result.length);
    return result;

  } catch (error) {
    console.error('获取智能推荐失败:', error);
    return [];
  }
};

const loadUserData = async () => {
  try {
    const savedHealthData = await getUserHealthData();
    if (savedHealthData) {
      healthForm.value = { ...healthForm.value, ...savedHealthData };
    }
    const savedPreferences = await getUserPreferences();
    if (savedPreferences) {
      preferencesForm.value = { ...preferencesForm.value, ...savedPreferences };
    }
    const ingredients = await getAllIngredients();
    console.log('加载的食材数据:', ingredients);
    allIngredients.value = ingredients;
  } catch (error) {
    console.error('加载用户数据失败:', error);
    // 如果食材加载失败，设置一个空数组确保组件不会崩溃
    allIngredients.value = [];
  }
};

const saveUserData = async () => {
  try {
    await saveUserHealthData({
      ...healthForm.value,
      bmi: bmi.value,
      bmiStatus: bmiStatus.value,
      dailyCalories: dailyCalories.value
    });
    await saveUserPreferences(preferencesForm.value);
  } catch (error) {
    console.error('保存用户数据失败:', error);
  }
};

// Enhanced recommendation function with fallback logic
const generateRecommendation = async () => {
  loading.value = true;
  try {
    await saveUserData();
    
    // --- PREPARE PAYLOAD ---
    // Convert ingredient IDs to names before sending to the backend
    const processedPreferences = JSON.parse(JSON.stringify(preferencesForm.value));
    
    const idToNameMap = new Map(allIngredients.value.map(item => [item.id, item.name]));

    if (processedPreferences.avoidedIngredients) {
      processedPreferences.avoidedIngredients = processedPreferences.avoidedIngredients.map(
        idOrName => idToNameMap.get(idOrName) || idOrName
      );
    }
    if (processedPreferences.favoriteIngredients) {
      processedPreferences.favoriteIngredients = processedPreferences.favoriteIngredients.map(
        idOrName => idToNameMap.get(idOrName) || idOrName
      );
    }
    // --- END PREPARE PAYLOAD ---

    // 使用改进的智能推荐算法
    console.log('开始生成推荐，健康数据:', {
      bmi: bmi.value,
      bmiStatus: bmiStatus.value,
      dailyCalories: dailyCalories.value
    });
    
    const smartRecipes = await getFallbackRecommendations(processedPreferences);
    recommendedRecipes.value = smartRecipes;
    hasGenerated.value = true;
    
    if (smartRecipes.length > 0) {
      ElMessage.success(`为您智能推荐了 ${smartRecipes.length} 道菜谱`);
    } else {
      ElMessage.warning('暂时无法生成推荐，请检查您的偏好设置或稍后重试');
    }
  } catch (error) {
    console.error('生成推荐失败:', error);
    ElMessage.error('生成推荐时发生错误，请稍后重试');
    recommendedRecipes.value = [];
    hasGenerated.value = true;
  } finally {
    loading.value = false;
  }
};

const viewRecipeDetail = (recipeId) => {
  router.push(`/recipe/${recipeId}`);
};

const onFavoriteChange = ({ recipe, isFavorite }) => {
  const actionText = isFavorite ? t('common.addedTo') : t('common.removedFrom');
  ElMessage.success(`${t('common.successfully')} ${actionText} ${t('common.favorites')}: "${recipe.name}"`);
};

onMounted(async () => {
  await loadUserData();
});

watch([() => healthForm.value.height, () => healthForm.value.weight, () => healthForm.value.age], () => {
  if (hasGenerated.value) {
    recommendedRecipes.value = [];
    hasGenerated.value = false;
  }
});
</script>

<style scoped>
.ai-recommend-page {
  padding: 20px !important; /* 添加内边距 */
  margin: 0 auto !important;
  width: 100% !important;
  max-width: 1440px !important; /* 限制最大宽度 */
  height: calc(100vh - 70px) !important; /* 减去导航栏高度 */
  overflow: visible !important;
  display: flex !important;
  justify-content: center !important;
  box-sizing: border-box !important;
}

.main-row {
  height: 100% !important;
  width: 100% !important;
  max-width: 1200px !important; /* 进一步限制内容宽度 */
  margin: 0 auto !important;
  padding: 0 !important;
  display: flex !important;
  flex: 1 !important;
  box-sizing: border-box !important;
  border-radius: 16px !important; /* 添加圆角 */
  overflow: visible !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important; /* 添加阴影 */
}

/* 两列布局 */
.health-col, .recommend-col {
  height: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
  border-right: 1px solid var(--el-border-color);
  display: flex !important;
  flex-direction: column !important;
  box-sizing: border-box !important;
  overflow: hidden;
}

.health-col {
  flex: 1.5 !important; /* 1.5份宽度 */
  min-width: 0;
}

.recommend-col {
  flex: 2.5 !important; /* 2.5份宽度 */
  border-right: none;
  min-width: 0;
}

/* 健康数据容器 - 使用美食展厅的紫色透明框架样式 */
.health-form-container {
  height: 100%;
  overflow-y: auto;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 8px 16px rgba(0, 0, 0, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
  border-radius: 24px !important;
  backdrop-filter: blur(10px) !important;
  position: relative !important;
  overflow: visible !important;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
  display: flex;
  flex-direction: column;
}

.health-form-container:hover {
  transform: translateY(-4px);
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.15),
    0 12px 24px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.health-form-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
}

.health-form-container .health-form {
  flex: 1;
  overflow-y: auto;
}

.health-header {
  padding: 20px 20px 0 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.5) !important; /* 透明化头部背景 */
  backdrop-filter: blur(8px) !important;
}

.health-header h2 {
  margin: 0 0 20px 0;
  font-size: 1.5rem;
  color: var(--el-text-color-primary);
  font-weight: 600;
}

.health-form {
  padding: 20px;
}

/* 优化表单布局 */
.health-form .el-form-item {
  margin-bottom: 16px;
}

.health-form .el-form-item__label {
  font-size: 14px;
  font-weight: 500;
  padding-bottom: 4px;
}

/* 单位样式优化 */
.unit {
  margin-left: 8px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  font-weight: 500;
}

/* 性别选择单选按钮毛玻璃样式 */
.health-form :deep(.el-radio-group .el-radio) {
  margin-right: 16px !important;
}

.health-form :deep(.el-radio-group .el-radio__input .el-radio__inner) {
  background: rgba(102, 126, 234, 0.1) !important;
  backdrop-filter: blur(8px) !important;
  border: 2px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  width: 18px !important;
  height: 18px !important;
}

.health-form :deep(.el-radio-group .el-radio__input:hover .el-radio__inner) {
  background: rgba(102, 126, 234, 0.2) !important;
  transform: scale(1.1) !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
}

.health-form :deep(.el-radio-group .el-radio__input.is-checked .el-radio__inner) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.8), rgba(118, 75, 162, 0.8)) !important;
  border-color: rgba(102, 126, 234, 0.8) !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
}

.health-form :deep(.el-radio-group .el-radio__input.is-checked .el-radio__inner::after) {
  background: white !important;
  width: 8px !important;
  height: 8px !important;
}

.health-form :deep(.el-radio-group .el-radio__label) {
  color: var(--el-text-color-primary) !important;
  font-weight: 500 !important;
  font-size: 14px !important;
  padding-left: 8px !important;
}

/* 饮食限制复选框横向布局 */
.dietary-restrictions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.dietary-restrictions .el-checkbox {
  margin-right: 0;
}

/* 复选框毛玻璃样式 */
.dietary-restrictions :deep(.el-checkbox__input .el-checkbox__inner) {
  background: rgba(102, 126, 234, 0.1) !important;
  backdrop-filter: blur(8px) !important;
  border: 2px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 4px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.dietary-restrictions :deep(.el-checkbox__input:hover .el-checkbox__inner) {
  background: rgba(102, 126, 234, 0.2) !important;
  transform: scale(1.1) !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
}

.dietary-restrictions :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.8), rgba(118, 75, 162, 0.8)) !important;
  border-color: rgba(102, 126, 234, 0.8) !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
}

.dietary-restrictions :deep(.el-checkbox__label) {
  color: var(--el-text-color-primary) !important;
  font-weight: 500 !important;
  font-size: 14px !important;
}

/* 小尺寸组件优化 - 毛玻璃风格 */
.health-form .el-input-number {
  width: 100%;
}

.health-form :deep(.el-input-number .el-input__inner) {
  padding-left: 8px;
  padding-right: 8px;
  background: rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 8px !important;
}

/* 数字输入框加减按钮毛玻璃样式 */
.health-form :deep(.el-input-number .el-input-number__increase),
.health-form :deep(.el-input-number .el-input-number__decrease) {
  background: rgba(102, 126, 234, 0.1) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 6px !important;
  color: var(--el-text-color-primary) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}

.health-form :deep(.el-input-number .el-input-number__increase:hover),
.health-form :deep(.el-input-number .el-input-number__decrease:hover) {
  background: rgba(102, 126, 234, 0.2) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
}

.health-form :deep(.el-input-number .el-input-number__increase:active),
.health-form :deep(.el-input-number .el-input-number__decrease:active) {
  transform: translateY(0) scale(0.95) !important;
}

/* 下拉选择框毛玻璃样式 */
.health-form :deep(.el-select .el-select__wrapper) {
  background: rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 8px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.health-form :deep(.el-select .el-select__wrapper:hover) {
  background: rgba(255, 255, 255, 0.15) !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
  transform: translateY(-1px) !important;
}

.health-form :deep(.el-select .el-select__wrapper.is-focused) {
  background: rgba(255, 255, 255, 0.2) !important;
  border-color: rgba(102, 126, 234, 0.6) !important;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
}

.health-form :deep(.el-select .el-select__selected-item) {
  color: var(--el-text-color-primary) !important;
}

.health-form :deep(.el-select .el-select__caret) {
  color: var(--el-text-color-regular) !important;
}

/* 多选下拉框样式 */
.health-form :deep(.el-select .el-select__wrapper .el-select__input) {
  color: var(--el-text-color-primary) !important;
}

.health-form :deep(.el-select .el-select__wrapper .el-select__placeholder) {
  color: var(--el-text-color-placeholder) !important;
}

/* 多选标签样式 */
.health-form :deep(.el-select .el-select__wrapper .el-select__tags .el-tag) {
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

.health-form :deep(.el-select .el-select__wrapper .el-select__tags .el-tag .el-tag__close) {
  color: var(--el-text-color-regular) !important;
  border-radius: 50% !important;
  transition: all 0.2s !important;
}

.health-form :deep(.el-select .el-select__wrapper .el-select__tags .el-tag .el-tag__close:hover) {
  background: rgba(255, 255, 255, 0.2) !important;
  color: var(--el-text-color-primary) !important;
}

/* 下拉菜单弹出层毛玻璃样式 - 使用 popper-class */
:global(.ai-recommend-select-popper.el-select-dropdown) {
  background: rgba(40, 35, 60, 0.75) !important;
  backdrop-filter: blur(20px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 16px !important;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.2),
    0 8px 16px rgba(0, 0, 0, 0.1) !important;
  padding: 8px !important;
}

:global(.ai-recommend-select-popper.el-select-dropdown .el-select-dropdown__item) {
  background: transparent !important;
  color: var(--el-text-color-primary) !important;
  border-radius: 10px !important;
  margin: 2px 0 !important;
  padding: 10px 14px !important;
  font-weight: 500 !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

:global(.ai-recommend-select-popper.el-select-dropdown .el-select-dropdown__item:hover) {
  background: rgba(102, 126, 234, 0.2) !important;
  transform: translateX(4px) !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
}

:global(.ai-recommend-select-popper.el-select-dropdown .el-select-dropdown__item.is-selected) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.4), rgba(118, 75, 162, 0.4)) !important;
  color: white !important;
  font-weight: 700 !important;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4) !important;
}

:global(.ai-recommend-select-popper.el-popper[data-popper-placement^="bottom"] .el-popper__arrow::before) {
  background: rgba(40, 35, 60, 0.75) !important;
  border-color: transparent !important;
}

/* 亮色模式下的下拉菜单 */
:global(html:not(.dark) .ai-recommend-select-popper.el-select-dropdown) {
  background: rgba(255, 255, 255, 0.9) !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 8px 16px rgba(0, 0, 0, 0.05) !important;
}

:global(html:not(.dark) .ai-recommend-select-popper.el-select-dropdown .el-select-dropdown__item) {
  color: rgba(30, 41, 59, 0.9) !important;
}

:global(html:not(.dark) .ai-recommend-select-popper.el-select-dropdown .el-select-dropdown__item:hover) {
  background: rgba(102, 126, 234, 0.1) !important;
  color: rgba(30, 41, 59, 1) !important;
}

:global(html:not(.dark) .ai-recommend-select-popper.el-select-dropdown .el-select-dropdown__item.is-selected) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
  color: rgba(30, 41, 59, 1) !important;
  font-weight: 700 !important;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2) !important;
}

:global(html:not(.dark) .ai-recommend-select-popper.el-popper[data-popper-placement^="bottom"] .el-popper__arrow::before) {
  background: rgba(255, 255, 255, 0.9) !important;
  border-color: transparent !important;
}

/* 深色模式下的下拉菜单 */
:global(.dark .ai-recommend-select-popper.el-select-dropdown) {
  background: rgba(20, 15, 40, 0.8) !important;
}

:global(.dark .ai-recommend-select-popper.el-select-dropdown .el-select-dropdown__item.is-selected) {
  color: white !important;
}

:global(.dark .ai-recommend-select-popper.el-popper[data-popper-placement^="bottom"] .el-popper__arrow::before) {
  background: rgba(20, 15, 40, 0.8) !important;
}

/* 生成推荐按钮样式 - 毛玻璃风格 */
.health-form .el-button {
  font-size: 15px;
  font-weight: 600;
  padding: 12px 20px;
  border-radius: 12px !important;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.8), rgba(118, 75, 162, 0.8)) !important;
  backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.health-form .el-button:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9)) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4) !important;
}

.health-form .el-button:active {
  transform: translateY(0) scale(0.98) !important;
}



/* 推荐结果容器 - 使用美食展厅的紫色透明框架样式 */
.recommendation-container {
  height: 100%;
  overflow-y: auto;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 8px 16px rgba(0, 0, 0, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
  border-radius: 24px !important;
  backdrop-filter: blur(10px) !important;
  position: relative !important;
  overflow: visible !important;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
  display: flex;
  flex-direction: column;
}

.recommendation-container:hover {
  transform: translateY(-4px);
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.15),
    0 12px 24px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.recommendation-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
}

.recommend-header {
  padding: 20px 20px 0 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.5) !important; /* 透明化头部背景 */
  backdrop-filter: blur(8px) !important;
}

.recommend-header .section-title {
  margin: 0 0 20px 0;
  font-size: 1.3rem;
  color: var(--el-text-color-primary);
}

.recommend-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .health-col, .recommend-col {
    border-right: none;
    border-bottom: 1px solid var(--el-border-color);
    flex: none;
    width: 100%;
  }
  
  .main-row {
    flex-direction: column;
  }
  
  .ai-recommend-page {
    height: auto;
    min-height: calc(100vh - 70px);
  }
}



.health-form h3 {
  margin-top: 16px;
  margin-bottom: 12px;
  font-size: 1.2rem;
  color: var(--el-text-color-primary);
  font-weight: 600;
}

.health-form h3:first-of-type {
  margin-top: 0;
}



.health-summary {
  margin-top: 18px;
  margin-bottom: 18px;
  padding: 18px;
  background: linear-gradient(135deg, var(--el-color-info-light-9) 0%, var(--el-color-primary-light-9) 100%);
  border-radius: 10px;
  border: 1px solid var(--el-color-info-light-6);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.health-summary h3 {
  margin-top: 0;
  margin-bottom: 14px;
  font-size: 1.3rem;
  color: var(--el-text-color-primary);
  font-weight: 700;
}

.summary-item {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  white-space: normal;
  font-size: 16px;
  line-height: 1.6;
}

.summary-item span:first-child {
  color: var(--el-text-color-regular);
  font-weight: 500;
}

.summary-item strong {
  margin: 0 6px;
  color: var(--el-color-primary);
  flex-shrink: 0;
  font-size: 17px;
  font-weight: 700;
}

.bmi-status {
  margin-left: 8px;
  flex-shrink: 0; /* 防止 tag 被压缩 */
}

.advice-box {
  margin-top: 16px;
  padding: 14px;
  background: linear-gradient(135deg, var(--el-fill-color-lighter) 0%, var(--el-color-info-light-9) 100%);
  border-radius: 8px;
  border-left: 4px solid var(--el-color-primary);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.advice-text {
  font-family: 'KaiTi', '楷体', '华文楷体', 'STKaiti', serif;
  font-size: 15px;
  color: var(--el-text-color-primary);
  line-height: 1.7;
  margin: 0;
  font-weight: 500;
  letter-spacing: 0.5px;
}



.recommendation-intro {
  margin-bottom: 20px;
  color: var(--el-text-color-secondary);
}

.recipe-col {
  margin-bottom: 20px;
}

.recommendation-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: transparent !important;
  border-radius: 8px;
  color: var(--el-text-color-secondary);
}

.placeholder-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  color: var(--el-text-color-placeholder);
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

/* 深色模式下的紫色透明框架 */
.dark .health-form-container,
.dark .recommendation-container {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.3),
    0 8px 16px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
}

/* 深色模式下的毛玻璃组件样式 */
.dark .health-form :deep(.el-input-number .el-input__inner) {
  background: rgba(31, 41, 55, 0.3) !important;
  border-color: rgba(255, 255, 255, 0.1) !important;
  color: var(--el-text-color-primary) !important;
}

.dark .health-form :deep(.el-input-number .el-input-number__increase),
.dark .health-form :deep(.el-input-number .el-input-number__decrease) {
  background: rgba(102, 126, 234, 0.15) !important;
  border-color: rgba(255, 255, 255, 0.1) !important;
}

.dark .health-form :deep(.el-radio-group .el-radio__input .el-radio__inner) {
  background: rgba(31, 41, 55, 0.3) !important;
  border-color: rgba(255, 255, 255, 0.15) !important;
}

.dark .dietary-restrictions :deep(.el-checkbox__input .el-checkbox__inner) {
  background: rgba(31, 41, 55, 0.3) !important;
  border-color: rgba(255, 255, 255, 0.15) !important;
}

.dark .health-form :deep(.el-select .el-select__wrapper) {
  background: rgba(31, 41, 55, 0.3) !important;
  border-color: rgba(255, 255, 255, 0.1) !important;
}

.dark .health-form :deep(.el-select .el-select__wrapper:hover) {
  background: rgba(31, 41, 55, 0.4) !important;
}

.dark .health-header,
.dark .recommend-header {
  background: rgba(31, 41, 55, 0.5) !important; /* 深色模式下的透明头部 */
  border-bottom: 1px solid rgba(75, 85, 99, 0.3);
}

/* 亮色模式的径向渐变 */
:root:not(.dark) .ai-recommend-page {
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