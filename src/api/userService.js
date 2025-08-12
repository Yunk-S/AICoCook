/**
 * 用户服务API
 */
import axios from 'axios';

/**
 * 获取用户健康数据
 * @returns {Promise<Object|null>} 健康数据
 */
export async function getUserHealthData() {
  return new Promise((resolve) => {
    setTimeout(() => {
      const data = localStorage.getItem('userHealthData');
      resolve(data ? JSON.parse(data) : null);
    }, 100);
  });
}

/**
 * 保存用户健康数据
 * @param {Object} data 健康数据
 * @returns {Promise<boolean>} 是否保存成功
 */
export async function saveUserHealthData(data) {
  return new Promise((resolve) => {
    setTimeout(() => {
      localStorage.setItem('userHealthData', JSON.stringify(data));
      resolve(true);
    }, 100);
  });
}

/**
 * 获取用户饮食偏好
 * @returns {Promise<Object|null>} 饮食偏好
 */
export async function getUserPreferences() {
  return new Promise((resolve) => {
    setTimeout(() => {
      const data = localStorage.getItem('userPreferences');
      resolve(data ? JSON.parse(data) : null);
    }, 100);
  });
}

/**
 * 保存用户饮食偏好
 * @param {Object} preferences 饮食偏好
 * @returns {Promise<boolean>} 是否保存成功
 */
export async function saveUserPreferences(preferences) {
  return new Promise((resolve) => {
    setTimeout(() => {
      localStorage.setItem('userPreferences', JSON.stringify(preferences));
      resolve(true);
    }, 100);
  });
}

/**
 * 获取用户收藏的菜谱列表
 * @param {boolean} full - 是否返回完整的菜谱对象
 * @returns {Array} 收藏的菜谱ID或对象列表
 */
export async function getFavoriteRecipes(full = false) {
  try {
    const response = await axios.get('/api/userdata/favorites');
    let favorites = response.data;
    if (typeof favorites === 'string') {
      favorites = JSON.parse(favorites || '[]');
    }
    if (!Array.isArray(favorites)) {
      favorites = [];
    }

  if (!full) {
      return favorites;
    }
    return favorites;
  } catch (error) {
    console.error('Error getting favorite recipes:', error);
    return [];
  }
}

/**
 * 添加菜谱到收藏
 * @param {Object} recipe 菜谱对象
 * @returns {Promise<boolean>} 是否添加成功
 */
export async function addToFavorites(recipe) {
  try {
    const favorites = await getFavoriteRecipes(true);
      if (!favorites.some(item => item.id === recipe.id)) {
        const simplifiedRecipe = {
          id: recipe.id,
          name: recipe.name,
          image: recipe.image,
          category: recipe.category,
          difficulty: recipe.difficulty,
        videoUrl: recipe.videoUrl,
          addedAt: new Date().toISOString()
        };
        favorites.push(simplifiedRecipe);
      await axios.post('/api/userdata/favorites', favorites);
      }
    return true;
  } catch (error) {
    console.error('Error adding to favorites:', error);
    return false;
  }
}

/**
 * 从收藏中移除菜谱
 * @param {string} recipeId 菜谱ID
 * @returns {Promise<boolean>} 是否移除成功
 */
export async function removeFromFavorites(recipeId) {
  try {
    const favorites = await getFavoriteRecipes(true);
      const updatedFavorites = favorites.filter(recipe => recipe.id !== recipeId);
    await axios.post('/api/userdata/favorites', updatedFavorites);
    return true;
  } catch (error) {
    console.error('Error removing from favorites:', error);
    return false;
  }
}

/**
 * 检查菜谱是否已收藏
 * @param {string} recipeId 菜谱ID
 * @returns {Promise<boolean>} 是否已收藏
 */
export async function isFavorite(recipeId) {
  try {
  const favorites = await getFavoriteRecipes();
  return favorites.some(recipe => recipe.id === recipeId);
  } catch (error) {
    console.error('Error checking favorite status:', error);
    return false;
  }
}

/**
 * 获取用户浏览历史
 * @param {boolean} full - 是否返回完整的菜谱对象和时间戳
 * @returns {Array} 浏览历史记录
 */
export async function getHistoryRecipes(full = false) {
  try {
    const response = await axios.get('/api/userdata/history');
    let history = response.data;
    if (typeof history === 'string') {
      history = JSON.parse(history || '[]');
    }
    if (!Array.isArray(history)) {
      history = [];
    }

  if (!full) {
    return history.map(item => ({
      id: item.id,
      name: item.name,
      image: item.image,
      category: item.category,
      viewedAt: item.viewedAt
    }));
  }
  return history;
  } catch (error) {
    console.error('Error getting history recipes:', error);
    return [];
  }
}

/**
 * 添加菜谱到浏览历史
 * @param {Object} recipe 菜谱对象
 * @returns {Promise<boolean>} 是否添加成功
 */
export async function addToHistory(recipe) {
  try {
    const history = await getHistoryRecipes(true);
      // 移除已存在的相同菜谱（如果有）
      const filteredHistory = history.filter(item => item.id !== recipe.id);
      
      // 只保存必要的信息
      const simplifiedRecipe = {
        id: recipe.id,
        name: recipe.name,
        image: recipe.image,
        category: recipe.category,
      difficulty: recipe.difficulty,
      videoUrl: recipe.videoUrl,
        viewedAt: new Date().toISOString()
      };
      
      // 添加到历史记录的开头
      filteredHistory.unshift(simplifiedRecipe);
      const limitedHistory = filteredHistory.slice(0, 50);
    await axios.post('/api/userdata/history', limitedHistory);
    return true;
  } catch (error) {
    console.error('Error adding to history:', error);
    return false;
  }
}

/**
 * 清空浏览历史
 * @returns {Promise<boolean>} 是否清空成功
 */
export async function clearHistory() {
  try {
    await axios.post('/api/userdata/history', []);
    return true;
  } catch (error) {
    console.error('Error clearing history:', error);
    return false;
  }
}

/**
 * 保存菜单组合到历史记录
 * @param {Object} mealCombination 菜单组合对象
 * @returns {Promise<boolean>} 是否保存成功
 */
export async function saveRecipeHistory(mealCombination) {
  // This function seems to be related to a different history list.
  // We will leave it as is, assuming it uses localStorage for a different purpose.
  return new Promise((resolve) => {
    setTimeout(() => {
      const history = JSON.parse(localStorage.getItem('mealCombinationHistory') || '[]');
      history.unshift(mealCombination);
      
      // 限制历史记录数量
      const limitedHistory = history.slice(0, 10);
      
      localStorage.setItem('mealCombinationHistory', JSON.stringify(limitedHistory));
      resolve(true);
    }, 200);
  });
} 