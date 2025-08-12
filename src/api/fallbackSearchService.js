/**
 * 后备搜索服务 - 当后端API不可用时使用前端搜索
 */
import { getAllRecipes } from '../data/recipes.js';

/**
 * 前端关键词搜索实现
 * @param {string} query 搜索关键词
 * @param {number} limit 结果数量限制
 * @returns {Promise<Object>} 搜索结果
 */
export async function fallbackSearch(query, limit = 600) {
  console.log('🔄 使用前端后备搜索:', query);
  
  try {
    const allRecipes = await getAllRecipes();
    
    if (!Array.isArray(allRecipes) || allRecipes.length === 0) {
      return {
        success: false,
        recipes: [],
        totalResults: 0,
        query: query.trim(),
        message: '没有可搜索的菜谱数据',
        error: '数据为空',
        timestamp: new Date().toISOString()
      };
    }

    const keywords = extractKeywords(query);
    console.log('提取关键词:', keywords);
    
    // 按匹配度进行评分
    const scoredRecipes = allRecipes.map(recipe => {
      let score = 0;
      
      keywords.forEach(keyword => {
        // 检查菜名 (权重最高)
        if (recipe.name && recipe.name.includes(keyword)) {
          score += 10;
        }
        
        // 检查食材
        if (recipe.stuff && Array.isArray(recipe.stuff)) {
          recipe.stuff.forEach(ingredient => {
            if (ingredient.includes(keyword)) {
              score += 5;
            }
          });
        }
        
        // 检查标签
        if (recipe.tags && Array.isArray(recipe.tags)) {
          recipe.tags.forEach(tag => {
            if (tag.includes(keyword)) {
              score += 3;
            }
          });
        }
        
        // 检查烹饪方法
        if (recipe.methods && recipe.methods.includes(keyword)) {
          score += 4;
        }
        
        // 检查厨具
        if (recipe.tools && Array.isArray(recipe.tools)) {
          recipe.tools.forEach(tool => {
            if (tool.includes(keyword)) {
              score += 2;
            }
          });
        }
      });
      
      return { recipe, score };
    });
    
    // 排序并返回得分高的结果
    const matchedRecipes = scoredRecipes
      .filter(item => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map(item => ({
        ...item.recipe,
        matchScore: item.score,
        image: item.recipe.image || `/images/${item.recipe.id.replace('recipe-', '')}.jpg` || '/images/recipe-placeholder.jpg'
      }));
    
    console.log(`✅ 前端搜索完成，找到 ${matchedRecipes.length} 个结果`);
    
    return {
      success: true,
      recipes: matchedRecipes,
      totalResults: matchedRecipes.length,
      query: query.trim(),
      message: `找到 ${matchedRecipes.length} 个相关菜谱 (前端搜索)`,
      analysis: {
        searchType: '前端关键词搜索',
        keywords: keywords,
        searchTime: Date.now(),
        matchedCount: matchedRecipes.length
      },
      error: null,
      timestamp: new Date().toISOString()
    };
    
  } catch (error) {
    console.error('❌ 前端搜索失败:', error);
    
    return {
      success: false,
      recipes: [],
      totalResults: 0,
      query: query.trim(),
      message: `前端搜索失败: ${error.message}`,
      analysis: null,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
}

/**
 * 从查询中提取关键词
 * @param {string} query 查询文本
 * @returns {Array<string>} 关键词数组
 */
function extractKeywords(query) {
  // 停用词列表
  const stopWords = new Set(['我想', '想要', '怎么', '如何', '可以', '能够', '一道', '做一道', '适合', '的', '了', '吗', '呢', '啊', '要', '是', '和', '或', '与']);
  
  return query
    .trim()
    .split(/[\s,，。.、!！?？:：;；]+/)
    .filter(word => word && word.length > 0 && !stopWords.has(word))
    .map(word => word.trim())
    .filter(Boolean);
}

/**
 * 搜索建议生成
 * @param {string} query 原始查询
 * @param {Array} results 搜索结果
 * @returns {Object} 建议对象
 */
export function generateSearchSuggestions(query, results) {
  const suggestions = [];
  
  if (results.length > 0) {
    // 从结果中提取常见标签作为建议
    const allTags = results.flatMap(recipe => recipe.tags || []);
    const tagCounts = {};
    
    allTags.forEach(tag => {
      tagCounts[tag] = (tagCounts[tag] || 0) + 1;
    });
    
    // 选择出现频率高的标签作为建议
    const topTags = Object.entries(tagCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3)
      .map(([tag]) => tag);
    
    suggestions.push(...topTags);
  }
  
  // 添加一些通用建议
  const commonSuggestions = ['家常菜', '素菜', '荤菜', '简单易做', '下饭菜'];
  suggestions.push(...commonSuggestions.filter(s => !suggestions.includes(s)).slice(0, 2));
  
  return {
    suggestedQueries: suggestions.slice(0, 5)
  };
}