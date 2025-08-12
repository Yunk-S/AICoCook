/**
 * 增强搜索服务 - 统一调用传统搜索和RAG智能问答
 */

import { searchRecipes, getSimilarRecipes, checkApiHealth } from './aiRecipeSearchService.js';
import { ragQuery, ragSearch, checkRagServiceHealth, getQuerySuggestions } from './ragService.js';

/**
 * 增强菜谱搜索 - 同时使用传统搜索和RAG系统
 * @param {string} query 用户搜索查询
 * @param {Object} options 搜索选项
 * @returns {Promise<Object>} 增强搜索结果
 */
export async function enhancedRecipeSearch(query, options = {}) {
  const {
    useRag = true,           // 是否使用RAG系统
    useLegacy = true,        // 是否使用传统搜索
    ragMaxResults = 5,       // RAG最大结果数
    includeDetails = false   // 是否包含搜索详情
  } = options;

  const results = {
    query,
    timestamp: new Date().toISOString(),
    ragResults: null,
    legacyResults: null,
    combinedResults: [],
    ragAnswer: null,
    searchMessage: '',
    success: false,
    errors: []
  };

  // 并行调用传统搜索和RAG搜索
  const promises = [];

  if (useRag) {
    promises.push(
      ragQuery(query, ragMaxResults, includeDetails)
        .then(ragResult => {
          results.ragResults = ragResult;
          if (ragResult.success) {
            results.ragAnswer = ragResult.answer;
            results.combinedResults.push(...(ragResult.results || []));
          } else {
            results.errors.push(`RAG搜索失败: ${ragResult.error}`);
          }
        })
        .catch(error => {
          results.errors.push(`RAG系统错误: ${error.message}`);
        })
    );
  }

  if (useLegacy) {
    promises.push(
      searchRecipes(query)
        .then(legacyResult => {
          results.legacyResults = legacyResult;
          if (legacyResult.recipes && legacyResult.recipes.length > 0) {
            results.combinedResults.push(...legacyResult.recipes);
          } else if (legacyResult.error) {
            results.errors.push(`传统搜索失败: ${legacyResult.error}`);
          }
        })
        .catch(error => {
          results.errors.push(`传统搜索错误: ${error.message}`);
        })
    );
  }

  // 等待所有搜索完成
  await Promise.all(promises);

  // 去重和排序结果
  results.combinedResults = deduplicateResults(results.combinedResults);
  
  // 设置成功状态和消息
  if (results.combinedResults.length > 0) {
    results.success = true;
    results.searchMessage = generateSearchMessage(results);
  } else if (results.errors.length > 0) {
    results.searchMessage = '搜索服务遇到问题，请稍后再试';
  } else {
    results.searchMessage = '未找到相关菜谱，请尝试其他关键词';
  }

  return results;
}

/**
 * 快速菜谱搜索 - 优先使用RAG，失败时降级到传统搜索
 * @param {string} query 搜索查询
 * @returns {Promise<Object>} 搜索结果
 */
export async function quickRecipeSearch(query) {
  try {
    // 首先尝试RAG搜索
    const ragResult = await ragSearch(query, 600);
    if (ragResult.success && ragResult.results.length > 0) {
      return {
        success: true,
        recipes: ragResult.results,
        source: 'rag',
        total: ragResult.total,
        message: `通过智能搜索找到 ${ragResult.total} 个相关菜谱`
      };
    }
  } catch (ragError) {
    console.warn('RAG搜索失败，尝试传统搜索:', ragError);
  }

  // RAG失败时使用传统搜索
  try {
    const legacyResult = await searchRecipes(query);
    if (legacyResult.recipes && legacyResult.recipes.length > 0) {
      return {
        success: true,
        recipes: legacyResult.recipes,
        source: 'legacy',
        total: legacyResult.recipes.length,
        message: legacyResult.message || `找到 ${legacyResult.recipes.length} 个相关菜谱`
      };
    }
  } catch (legacyError) {
    console.error('传统搜索也失败了:', legacyError);
  }

  return {
    success: false,
    recipes: [],
    source: 'none',
    total: 0,
    message: '搜索服务暂时不可用，请稍后再试'
  };
}

/**
 * 获取智能搜索建议
 * @param {string} prefix 输入前缀
 * @returns {Promise<Array>} 建议列表
 */
export async function getSmartSuggestions(prefix) {
  if (!prefix || prefix.length < 1) return [];

  try {
    const ragSuggestions = await getQuerySuggestions(prefix, 8);
    if (ragSuggestions.success && ragSuggestions.suggestions.length > 0) {
      return ragSuggestions.suggestions;
    }
  } catch (error) {
    console.warn('RAG建议获取失败:', error);
  }

  // 如果RAG建议失败，返回一些通用建议
  const commonSuggestions = [
    '川菜', '粤菜', '湘菜', '家常菜', '素食', 
    '快手菜', '汤品', '甜点', '早餐', '减脂餐'
  ];
  
  return commonSuggestions.filter(s => 
    s.toLowerCase().includes(prefix.toLowerCase())
      ).slice(0, 600);
}

/**
 * 检查所有搜索服务的健康状态
 * @returns {Promise<Object>} 服务状态
 */
export async function checkAllServicesHealth() {
  const [ragHealthy, legacyHealthy] = await Promise.all([
    checkRagServiceHealth().catch(() => false),
    checkApiHealth().catch(() => false)
  ]);

  return {
    rag: ragHealthy,
    legacy: legacyHealthy,
    overall: ragHealthy || legacyHealthy,
    preferredService: ragHealthy ? 'rag' : (legacyHealthy ? 'legacy' : 'none')
  };
}

/**
 * 获取相关菜谱 - 增强版
 * @param {string} recipeId 菜谱ID
 * @param {string} recipeName 菜谱名称（用于RAG搜索）
 * @returns {Promise<Array>} 相关菜谱列表
 */
export async function getEnhancedSimilarRecipes(recipeId, recipeName = '') {
  const results = [];

  // 并行调用传统相似搜索和RAG搜索
  const promises = [];

  // 传统相似搜索
  promises.push(
    getSimilarRecipes(recipeId, 8)
      .then(similarRecipes => results.push(...similarRecipes))
      .catch(error => console.warn('传统相似搜索失败:', error))
  );

  // 如果有菜谱名称，使用RAG搜索相关菜谱
  if (recipeName) {
    const searchQuery = `类似${recipeName}的菜谱`;
    promises.push(
              ragSearch(searchQuery, 600)
        .then(ragResult => {
          if (ragResult.success) {
            results.push(...ragResult.results);
          }
        })
        .catch(error => console.warn('RAG相似搜索失败:', error))
    );
  }

  await Promise.all(promises);

  // 去重并限制数量
  return deduplicateResults(results).slice(0, 600);
}

/**
 * 去重搜索结果
 * @param {Array} results 搜索结果数组
 * @returns {Array} 去重后的结果
 */
function deduplicateResults(results) {
  const seen = new Set();
  return results.filter(recipe => {
    const key = recipe.id || recipe.recipe_id || recipe.title || recipe.name;
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

/**
 * 生成搜索消息
 * @param {Object} results 搜索结果
 * @returns {string} 搜索消息
 */
function generateSearchMessage(results) {
  const totalResults = results.combinedResults.length;
  const hasRag = results.ragResults?.success;
  const hasLegacy = results.legacyResults?.recipes?.length > 0;

  if (hasRag && hasLegacy) {
    return `智能搜索找到 ${totalResults} 个相关菜谱`;
  } else if (hasRag) {
    return `通过AI问答找到 ${totalResults} 个相关菜谱`;
  } else if (hasLegacy) {
    return `通过关键词搜索找到 ${totalResults} 个相关菜谱`;
  } else {
    return `找到 ${totalResults} 个相关菜谱`;
  }
}

// 导出兼容性函数，保持向后兼容
export { searchRecipes as legacySearchRecipes } from './aiRecipeSearchService.js';
export { ragQuery, ragSearch } from './ragService.js';

// 设置默认搜索函数
export const searchRecipes = quickRecipeSearch;