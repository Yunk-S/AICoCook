/**
 * 菜谱相关API服务
 */
import {
  getAllRecipes,
  getRecipeById,
  getRecipesByCategory,
  getRecipesByIngredients,
  getRecipesByCookwares,
  getRandomMealCombination,
  searchRecipes
} from '../data/recipes';

import { allIngredients } from '../data/ingredients';
import { cookwares } from '../data/cookwares';
import dataCache, { CACHE_KEYS } from '../utils/dataCache';

/**
 * 获取所有菜谱
 */
export async function getAllRecipesService() {
  try {
    // 检查缓存
    const cachedData = dataCache.get(CACHE_KEYS.ALL_RECIPES);
    if (cachedData) {
      return cachedData;
    }
    
    console.log('🔄 RecipeService: 开始获取菜谱数据...');
    const recipes = await getAllRecipes();
    
    // 确保返回有效数据
    if (!Array.isArray(recipes)) {
      console.error('菜谱数据格式错误，不是数组:', recipes);
      return [];
    }
    
    if (recipes.length === 0) {
      console.warn('⚠️ 获取到的菜谱数据为空');
      return [];
    }
    
    // 为每个菜谱添加图片
    const recipesWithImages = recipes.map(recipe => ({
      ...recipe,
      image: recipe.image || `/images/${recipe.id.replace('recipe-', '')}.jpg` || '/images/recipe-placeholder.jpg'
    }));
    
    // 设置缓存
    dataCache.set(CACHE_KEYS.ALL_RECIPES, recipesWithImages);
    
    console.log(`✅ RecipeService: 成功加载 ${recipesWithImages.length} 个菜谱`);
    return recipesWithImages;
  } catch (error) {
    console.error('❌ RecipeService: 加载菜谱数据失败:', error);
    return [];
  }
}

/**
 * 清除菜谱缓存
 */
export function clearRecipeCache() {
  dataCache.delete(CACHE_KEYS.ALL_RECIPES);
  dataCache.delete(CACHE_KEYS.TRENDING_RECIPES);
}

/**
 * 清除所有缓存
 */
export function clearAllCache() {
  dataCache.clear();
}

/**
 * 清除食材缓存
 */
export function clearIngredientsCache() {
  dataCache.delete(CACHE_KEYS.ALL_INGREDIENTS);
  console.log('🗑️ 食材缓存已清除');
}

// 直接导出数据层函数，以便视图层可以直接使用
export { getAllRecipes, getRecipeById, searchRecipes, getRandomMealCombination };

/**
 * 获取菜谱详情
 * @param {string} id 菜谱ID
 */
export async function getRecipeDetailsService(id) {
  const recipe = await getRecipeById(id);
  return recipe;
}

/**
 * 根据类别获取菜谱
 * @param {string} category 类别
 */
export async function getRecipesByCategoryService(category) {
  return getRecipesByCategory(category);
}

/**
 * 获取热门菜谱
 * @param {number} limit 返回数量限制
 * @returns {Promise<Array>} 热门菜谱列表
 */
export async function getTrendingRecipes(limit = 8) {
  const cacheKey = `${CACHE_KEYS.TRENDING_RECIPES}:${limit}`;
  const cachedData = dataCache.get(cacheKey);
  if (cachedData) {
    return cachedData;
  }
  
  const recipes = await getAllRecipes();
  
  // 模拟热门菜谱算法 - 在实际应用中，这可能基于用户浏览量、收藏数等
  // 这里简单地按照菜谱的某些属性进行排序
  const sortedRecipes = recipes.sort((a, b) => {
    // 优先考虑有图片的菜谱
    const hasImageA = a.image ? 1 : 0;
    const hasImageB = b.image ? 1 : 0;
    if (hasImageB !== hasImageA) return hasImageB - hasImageA;
    
    // 按受欢迎程度排序
    const popularityA = a.popularity || 0;
    const popularityB = b.popularity || 0;
    if (popularityB !== popularityA) return popularityB - popularityA;
    
    // 如果都没有受欢迎度数据，则按照食材数量排序（食材越多可能越复杂/特别）
    const ingredientsA = a.stuff ? a.stuff.length : 0;
    const ingredientsB = b.stuff ? b.stuff.length : 0;
    return ingredientsB - ingredientsA;
  });
  
  const result = sortedRecipes.slice(0, limit);
  
  // 缓存结果
  dataCache.set(cacheKey, result, 3 * 60 * 1000); // 3分钟缓存
  
  return result;
}

/**
 * 根据食材和厨具匹配菜谱
 * @param {Array<string>} ingredientIds 食材ID数组
 * @param {Array<string>} cookwareIds 厨具ID数组
 * @param {string} matchingMode 匹配模式：'fuzzy'（模糊）, 'strict'（严格）, 'survival'（生存）
 * @returns {Promise<Array>} 匹配的菜谱
 */
export async function getRecipesByIngredientsAndCookwares(ingredientIds = [], cookwareIds = [], matchingMode = 'fuzzy') {
  try {
    // 如果没有选择食材和厨具，则返回空数组
    if (ingredientIds.length === 0 && cookwareIds.length === 0) {
      return [];
    }
    
    console.log('🔍 开始匹配菜谱，食材ID:', ingredientIds, '厨具ID:', cookwareIds, '模式:', matchingMode);
    
    const allRecipes = await getAllRecipes();
    console.log('📚 获取到菜谱数量:', allRecipes.length);
    
    if (!Array.isArray(allRecipes)) {
      console.error('❌ allRecipes 不是数组:', allRecipes);
      return [];
    }
    
    let matchedRecipes = [];
    
    // 转换食材ID为名称，因为菜谱中存储的是食材名称
    const selectedIngredients = ingredientIds.map(id => {
      const ingredient = allIngredients.find(item => item.id === id);
      return ingredient ? ingredient.name : '';
    }).filter(Boolean);
    
    // 转换厨具ID为名称
    const selectedCookwares = cookwareIds.map(id => {
      const cookware = cookwares.find(item => item.id === id);
      return cookware ? cookware.name : '';
    }).filter(Boolean);
    
    console.log('🥬 选择的食材:', selectedIngredients);
    console.log('🍳 选择的厨具:', selectedCookwares);
  
  // 根据匹配模式进行筛选
  switch (matchingMode) {
    case 'strict':
      // 严格模式：必须包含所有选定的食材和厨具
      matchedRecipes = allRecipes.filter(recipe => {
        // 检查食材匹配
        const hasAllIngredients = selectedIngredients.length === 0 || 
          selectedIngredients.every(ingredientName => 
            recipe.stuff && recipe.stuff.some(recipeIngredient => 
              recipeIngredient.includes(ingredientName) || ingredientName.includes(recipeIngredient)
            )
          );
        
        // 检查厨具匹配
        const hasAllCookwares = selectedCookwares.length === 0 || 
          selectedCookwares.every(cookwareName => 
            recipe.tools && recipe.tools.some(recipeCookware => 
              recipeCookware.includes(cookwareName) || cookwareName.includes(recipeCookware)
            )
          );
        
        return hasAllIngredients && hasAllCookwares;
      });
      break;
      
    case 'survival':
      // 生存模式：仅使用选定的食材和厨具（不能使用未选择的）
      matchedRecipes = allRecipes.filter(recipe => {
        // 检查食材是否仅使用选定的
        const onlyUsesSelectedIngredients = recipe.stuff && recipe.stuff.every(recipeIngredient => 
          selectedIngredients.some(ingredientName => 
            recipeIngredient.includes(ingredientName) || ingredientName.includes(recipeIngredient)
          )
        );
        
        // 检查厨具是否仅使用选定的
        const onlyUsesSelectedCookwares = !recipe.tools || recipe.tools.every(recipeCookware => 
          selectedCookwares.some(cookwareName => 
            recipeCookware.includes(cookwareName) || cookwareName.includes(recipeCookware)
          )
        );
        
        return onlyUsesSelectedIngredients && onlyUsesSelectedCookwares;
      });
      break;
      
    default: // fuzzy 模式
      // 模糊模式：包含部分选定的食材和厨具即可
      matchedRecipes = allRecipes.map(recipe => {
        // 计算匹配的食材数量
        let matchedIngredients = 0;
        let matchedCookwares = 0;
        
        // 计算匹配的食材
        if (recipe.stuff && selectedIngredients.length > 0) {
          selectedIngredients.forEach(ingredientName => {
            if (recipe.stuff.some(recipeIngredient => 
              recipeIngredient.includes(ingredientName) || ingredientName.includes(recipeIngredient)
            )) {
              matchedIngredients++;
            }
          });
        }
        
        // 计算匹配的厨具
        if (recipe.tools && selectedCookwares.length > 0) {
          selectedCookwares.forEach(cookwareName => {
            if (recipe.tools.some(recipeCookware => 
              recipeCookware.includes(cookwareName) || cookwareName.includes(recipeCookware)
            )) {
              matchedCookwares++;
            }
          });
        }
        
        // 计算缺失的食材和厨具
        const missingItems = [];
        
        if (recipe.stuff) {
          recipe.stuff.forEach(recipeIngredient => {
            if (!selectedIngredients.some(ingredientName => 
              recipeIngredient.includes(ingredientName) || ingredientName.includes(recipeIngredient)
            )) {
              // 找到对应的食材对象
              const ingredient = allIngredients.find(item => 
                item.name === recipeIngredient || 
                (item.alias && item.alias.includes(recipeIngredient))
              );
              
              if (ingredient && !missingItems.some(item => item.id === ingredient.id)) {
                missingItems.push({
                  id: ingredient.id,
                  name: ingredient.name,
                  type: 'ingredient'
                });
              } else if (!ingredient && !missingItems.some(item => item.name === recipeIngredient)) {
                missingItems.push({
                  id: `ingredient-${recipeIngredient}`,
                  name: recipeIngredient,
                  type: 'ingredient'
                });
              }
            }
          });
        }
        
        if (recipe.tools) {
          recipe.tools.forEach(recipeCookware => {
            if (!selectedCookwares.some(cookwareName => 
              recipeCookware.includes(cookwareName) || cookwareName.includes(recipeCookware)
            )) {
              // 找到对应的厨具对象
              const cookware = cookwares.find(item => item.name === recipeCookware);
              
              if (cookware && !missingItems.some(item => item.id === cookware.id)) {
                missingItems.push({
                  id: cookware.id,
                  name: cookware.name,
                  type: 'cookware'
                });
              } else if (!cookware && !missingItems.some(item => item.name === recipeCookware)) {
                missingItems.push({
                  id: `cookware-${recipeCookware}`,
                  name: recipeCookware,
                  type: 'cookware'
                });
              }
            }
          });
        }
        
        // 计算匹配分数
        const totalIngredients = selectedIngredients.length;
        const totalCookwares = selectedCookwares.length;
        const totalSelected = totalIngredients + totalCookwares;
        
        let matchScore = 0;
        if (totalSelected > 0) {
          // 食材匹配权重占70%，厨具匹配权重占30%
          if (totalIngredients > 0) {
            matchScore += (matchedIngredients / totalIngredients) * 0.7;
          }
          
          if (totalCookwares > 0) {
            matchScore += (matchedCookwares / totalCookwares) * 0.3;
          }
          
          // 如果没有选择食材或厨具，则相应权重分配给另一个
          if (totalIngredients === 0 && totalCookwares > 0) {
            matchScore = matchedCookwares / totalCookwares;
          } else if (totalCookwares === 0 && totalIngredients > 0) {
            matchScore = matchedIngredients / totalIngredients;
          }
        }
        
        // 添加随机性避免所有菜谱都显示相同进度条
        const randomizedScore = Math.min(matchScore + (Math.random() * 0.15 - 0.075), 1);
        const finalScore = Math.max(randomizedScore, 0.2); // 最低20%

        return {
          ...recipe,
          matchScore: finalScore,
          matchedIngredients,
          matchedCookwares,
          missingItems
        };
      }).filter(recipe => recipe.matchScore > 0)
        .sort((a, b) => b.matchScore - a.matchScore);
  }
  
  console.log('✅ 匹配完成，找到菜谱数量:', matchedRecipes.length);
  return matchedRecipes;
  
  } catch (error) {
    console.error('❌ 匹配菜谱时发生错误:', error);
    return [];
  }
}

/**
 * 随机获取一组搭配的菜谱（一荤一素一汤一主食）
 * @returns {Promise<Object>} 随机菜谱组合
 */
export async function getRandomMealCombinationService() {
  return getRandomMealCombination();
}

/**
 * 获取所有食材
 * @returns {Promise<Array>} 食材列表
 */
export async function getAllIngredients() {
  const cachedData = dataCache.get(CACHE_KEYS.ALL_INGREDIENTS);
  if (cachedData) {
    return cachedData;
  }
  
  dataCache.set(CACHE_KEYS.ALL_INGREDIENTS, allIngredients, 10 * 60 * 1000); // 10分钟缓存
  return allIngredients;
}

/**
 * 获取所有厨具
 * @returns {Promise<Array>} 厨具列表
 */
export async function getAllCookwares() {
  const cachedData = dataCache.get(CACHE_KEYS.ALL_COOKWARES);
  if (cachedData) {
    return cachedData;
  }
  
  dataCache.set(CACHE_KEYS.ALL_COOKWARES, cookwares, 10 * 60 * 1000); // 10分钟缓存
  return cookwares;
}

/**
 * 搜索菜谱
 * @param {Object} filters 筛选条件
 * @returns {Promise<Array>} 搜索结果
 */
export async function searchRecipesService(filters = {}) {
  return searchRecipes(filters);
}

/**
 * 获取相关菜谱
 * @param {string} recipeId 菜谱ID
 * @param {number} limit 返回数量限制
 * @returns {Promise<Array>} 相关菜谱列表
 */
export async function getRelatedRecipes(recipeId, limit = 4) {
  // 获取当前菜谱
  const currentRecipe = await getRecipeById(recipeId);
  if (!currentRecipe) return [];
  
  const allRecipes = await getAllRecipes();
  
  // 根据相似度评分，并选出最高分的菜谱
  const relatedRecipes = allRecipes
    .filter(recipe => recipe.id !== recipeId) // 排除当前菜谱
    .map(recipe => {
      let score = 0;
      
      // 1. 共享食材评分 (权重最高)
      if (currentRecipe.stuff && recipe.stuff) {
        const currentIngredients = new Set(currentRecipe.stuff);
        const commonIngredients = recipe.stuff.filter(ingredient => currentIngredients.has(ingredient));
        score += commonIngredients.length * 5; // 每个共享食材得5分
      }
      
      // 2. 菜系相同评分
      if (currentRecipe.cuisine && recipe.cuisine === currentRecipe.cuisine) {
        score += 3; // 菜系相同得3分
      }

      // 3. 类别/标签相似度评分
      if (currentRecipe.category && recipe.category === currentRecipe.category) {
        score += 2; // 类别相同得2分
      }
      
      return { ...recipe, score };
    })
    .filter(recipe => recipe.score > 0) // 只保留有一定相似度的
    .sort((a, b) => b.score - a.score) // 按分数从高到低排序
    .slice(0, limit); // 取前4个
  
  // 如果评分后仍然没有结果，则随机推荐4个菜谱作为备选
  if (relatedRecipes.length === 0) {
    return allRecipes
      .filter(recipe => recipe.id !== recipeId)
      .sort(() => 0.5 - Math.random())
      .slice(0, limit);
  }

  return relatedRecipes;
}

/**
 * AI搜索菜谱
 * @param {string} query 自然语言查询
 */
export async function aiSearchRecipes(query) {
  // 未来可以接入LLM进行处理，目前简单实现关键词匹配
  // 提取可能的关键词
  const keywords = extractKeywords(query);
  
  // 获取所有菜谱
  const allRecipes = await getAllRecipes();
  
  // 按匹配度进行评分
  const scoredRecipes = allRecipes.map(recipe => {
    let score = 0;
    
    // 检查菜名
    keywords.forEach(keyword => {
      if (recipe.name.includes(keyword)) {
        score += 3;
      }
      
      // 检查食材
      if (recipe.stuff.some(stuff => stuff.includes(keyword))) {
        score += 2;
      }
      
      // 检查标签
      if (recipe.tags && recipe.tags.some(tag => tag.includes(keyword))) {
        score += 2;
      }
    });
    
    return { recipe, score };
  });
  
  // 排序并返回得分高的结果
  return scoredRecipes
    .filter(item => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .map(item => item.recipe)
    .slice(0, 600);
}

/**
 * 从自然语言查询中提取关键词
 * @param {string} query 查询文本
 * @returns {Array} 关键词数组
 */
function extractKeywords(query) {
  // 简单实现，未来可以接入NLP服务优化
  const stopWords = ['我想', '想要', '怎么', '如何', '可以', '能够', '一道', '做一道', '适合', '的', '了', '吗', '呢', '啊'];
  
  return query
    .split(/\s+|[,，。.、!！?？:：;；]/)
    .filter(word => word && word.length > 1 && !stopWords.includes(word));
} 