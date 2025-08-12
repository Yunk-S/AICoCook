/**
 * 关键词菜谱搜索服务 - 调用Python后端搜索引擎API
 * 基于关键词提炼和菜名匹配的高效搜索
 * 
 * 更新版本：增强错误处理、连接重试、状态管理
 */

// API配置
const API_CONFIG = {
  BASE_URL: '/api/search',
  TIMEOUT: 15000,  // 15秒超时
  MAX_RETRIES: 1,  // 减少重试次数
  RETRY_DELAY: 1000  // 1秒延迟
};

// 连接状态管理
let connectionState = {
  isHealthy: false,
  lastCheck: null,
  errorCount: 0
};

/**
 * 简化的HTTP请求函数（无AbortController）
 * @param {string} url 请求URL
 * @param {Object} options 请求选项
 * @returns {Promise<Response>} 响应对象
 */
async function makeRequest(url, options = {}) {
  console.log(`🚀 发起简化请求:`, url);
  console.log('📤 请求选项:', { ...options, body: options.body ? 'JSON数据' : undefined });
  
  try {
    console.log('📡 正在发送请求...');
    const response = await fetch(url, options);
    
    console.log(`📥 收到响应: ${response.status} ${response.statusText}`);
    console.log(`📡 响应URL: ${response.url}`);
    
    return response;
    
  } catch (error) {
    console.error(`❌ 请求失败:`, error.name, error.message);
    throw error;
  }
}

/**
 * 菜谱关键词搜索
 * @param {string} query 用户搜索查询
 * @param {number} limit 结果数量限制，默认600
 * @returns {Promise<Object>} 搜索结果
 */
export async function searchRecipes(query, limit = 600) {
  const startTime = Date.now();
  console.log('🔍 关键词搜索开始 - 查询内容:', query);
  console.log('📡 API路径:', `${API_CONFIG.BASE_URL}/search`);
  
  // 参数验证
  if (!query || typeof query !== 'string') {
    return createErrorResult(query, '搜索查询不能为空');
  }
  
  const cleanQuery = query.trim();
  if (!cleanQuery) {
    return createErrorResult(query, '搜索查询不能为空');
  }
  
  try {
    const requestData = { 
      query: cleanQuery, 
      limit: Math.max(1, Math.min(limit, 600)) // 限制范围 1-600
    };
    console.log('📤 发送请求数据:', requestData);
    
    // 使用带重试的请求函数
    const response = await makeRequest(`${API_CONFIG.BASE_URL}/search`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json'
      },
      body: JSON.stringify(requestData)
    });
    
    console.log('📥 响应状态:', response.status, response.statusText);
    console.log('📥 响应URL:', response.url);
    
    if (!response.ok) {
      let errorText = `HTTP ${response.status}`;
      try {
        const text = await response.text();
        if (text) {
          const parsed = JSON.parse(text);
          errorText = parsed.error || parsed.message || text;
        }
      } catch (e) {
        // 忽略解析错误，使用默认错误信息
      }
      
      connectionState.errorCount++;
      throw new Error(`搜索请求失败: ${errorText}`);
    }
    
    const result = await response.json();
    console.log('📋 后端返回结果:', result);
    
    // 检查后端返回的错误
    if (result.error) {
      throw new Error(result.error);
    }
    
    // 更新连接状态
    connectionState.isHealthy = true;
    connectionState.errorCount = 0;
    connectionState.lastCheck = Date.now();
    
    // 转换后端格式到前端期望格式
    const formattedResult = createSuccessResult(result, cleanQuery, Date.now() - startTime);
    
    console.log('✅ 格式化后结果:', formattedResult);
    return formattedResult;
    
  } catch (error) {
    console.error('❌ 关键词搜索失败:', error);
    connectionState.errorCount++;
    connectionState.isHealthy = false;
    
    return createErrorResult(cleanQuery, error.message || '搜索服务暂时不可用，请稍后再试');
  }
}

/**
 * 创建成功结果
 * @param {Object} backendResult 后端返回结果
 * @param {string} query 查询字符串
 * @param {number} searchTime 搜索耗时（毫秒）
 * @returns {Object} 格式化的成功结果
 */
function createSuccessResult(backendResult, query, searchTime) {
  const results = backendResult.results || [];
  return {
    success: true,
    recipes: results,
    message: `找到 ${backendResult.total || results.length} 个相关菜谱`,
    totalResults: backendResult.total || results.length,
    query: backendResult.query || query,
    analysis: {
      searchType: '关键词搜索',
      matchedKeywords: backendResult.matched_keywords || [],
      searchTime: searchTime,
      backendSearchTime: backendResult.search_time || null
    },
    searchTerms: [query],
    error: null,
    timestamp: new Date().toISOString()
  };
}

/**
 * 创建错误结果
 * @param {string} query 查询字符串
 * @param {string} errorMessage 错误信息
 * @returns {Object} 格式化的错误结果
 */
function createErrorResult(query, errorMessage) {
  return {
    success: false,
    recipes: [],
    analysis: null,
    searchTerms: [query || ''],
    error: errorMessage,
    message: '搜索服务暂时不可用，请稍后再试',
    totalResults: 0,
    timestamp: new Date().toISOString()
  };
}

/**
 * 获取搜索建议（基于关键词匹配）
 * @param {string} query 用户查询
 * @param {Array} searchResults 搜索结果
 * @returns {Promise<Object>} 搜索建议
 */
export async function getSearchSuggestions(query, searchResults = []) {
  // 基于关键词生成搜索建议（本地实现，无需后端）
  try {
    const suggestions = [];
    
    if (query && query.length > 0) {
      // 生成基于查询的建议
      suggestions.push(
        `${query}的做法`,
        `简单${query}`,
        `家常${query}`,
        `${query}食谱`,
        `${query}怎么做`
      );
      
      // 如果有搜索结果，基于结果生成更多建议
      if (searchResults.length > 0) {
        const cuisines = [...new Set(searchResults.map(r => r.cuisine).filter(Boolean))];
        const categories = [...new Set(searchResults.map(r => r.category).filter(Boolean))];
        
        cuisines.slice(0, 2).forEach(cuisine => {
          suggestions.push(`${cuisine}${query}`);
        });
        
        categories.slice(0, 2).forEach(category => {
          suggestions.push(`${category}${query}`);
        });
      }
    }
    
    return {
      success: true,
      suggestedQueries: suggestions.slice(0, 6), // 最多6个建议
      analysis: {
        searchType: '关键词建议',
        queryLength: query.length,
        resultCount: searchResults.length
      }
    };
  } catch (error) {
    console.error('生成搜索建议失败:', error);
    return {
      success: false,
      suggestedQueries: [],
      analysis: null
    };
  }
}

/**
 * 检查搜索引擎API服务健康状态
 * @param {boolean} useCache 是否使用缓存结果
 * @returns {Promise<Object>} 服务状态信息
 */
export async function checkApiHealth(useCache = true) {
  console.log('🔍 检查关键词搜索引擎健康状态:', API_CONFIG.BASE_URL);
  
  // 如果使用缓存且最近检查过（5分钟内），直接返回缓存结果
  const now = Date.now();
  if (useCache && connectionState.lastCheck && (now - connectionState.lastCheck) < 300000) {
    console.log('📋 使用缓存的健康检查结果:', connectionState.isHealthy);
    return {
      isHealthy: connectionState.isHealthy,
      status: connectionState.isHealthy ? 'healthy' : 'error',
      message: connectionState.isHealthy ? '服务运行正常（缓存）' : '服务不可用（缓存）',
      details: connectionState.isHealthy ? {
        totalRecipes: 0,
        indexedKeywords: 0,
        timestamp: new Date(connectionState.lastCheck).toISOString(),
        cached: true
      } : null
    };
  }
  
  try {
    // 使用重试机制进行健康检查
    const response = await makeRequest(`${API_CONFIG.BASE_URL}/health`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    
    console.log('📡 健康检查响应状态:', response.status);
    
    if (!response.ok) {
      console.log('❌ 健康检查失败，状态码:', response.status);
      connectionState.isHealthy = false;
      connectionState.errorCount++;
      connectionState.lastCheck = now;
      
      return {
        isHealthy: false,
        status: 'error',
        message: `服务响应错误: ${response.status}`,
        details: null
      };
    }
    
    const result = await response.json();
    console.log('📋 健康检查结果:', result);
    
    const isHealthy = result.status === 'healthy';
    console.log('✅ 搜索引擎健康状态:', isHealthy);
    
    // 更新连接状态
    connectionState.isHealthy = isHealthy;
    connectionState.lastCheck = now;
    if (isHealthy) {
      connectionState.errorCount = 0;
    }
    
    return {
      isHealthy: isHealthy,
      status: result.status,
      message: result.message || '服务运行正常',
      details: {
        totalRecipes: result.total_recipes || 0,
        indexedKeywords: result.indexed_keywords || 0,
        errorCount: connectionState.errorCount,
        timestamp: new Date().toISOString(),
        cached: false
      }
    };
  } catch (error) {
    console.error('💥 健康检查失败:', error);
    connectionState.isHealthy = false;
    connectionState.errorCount++;
    connectionState.lastCheck = now;
    
    let status = 'error';
    let message = error.message || '连接失败';
    
    if (error.name === 'AbortError') {
      console.log('⏰ 健康检查超时');
      status = 'timeout';
      message = '服务响应超时';
    }
    
    return {
      isHealthy: false,
      status: status,
      message: message,
      details: {
        errorCount: connectionState.errorCount,
        lastError: error.message,
        timestamp: new Date().toISOString()
      }
    };
  }
}

/**
 * 获取当前连接状态
 * @returns {Object} 连接状态信息
 */
export function getConnectionState() {
  return {
    ...connectionState,
    lastCheckFormatted: connectionState.lastCheck ? 
      new Date(connectionState.lastCheck).toLocaleString('zh-CN') : null
  };
}

/**
 * 重置连接状态
 */
export function resetConnectionState() {
  connectionState.isHealthy = false;
  connectionState.lastCheck = null;
  connectionState.errorCount = 0;
  console.log('🔄 连接状态已重置');
}

/**
 * 获取搜索统计信息
 * @returns {Promise<Object>} 统计信息
 */
export async function getSearchStats() {
  try {
    const healthInfo = await checkApiHealth();
    if (healthInfo.isHealthy && healthInfo.details) {
      return {
        success: true,
        totalRecipes: healthInfo.details.totalRecipes,
        indexedKeywords: healthInfo.details.indexedKeywords,
        searchEngine: '关键词搜索引擎',
        version: '2.0',
        features: [
          '中文分词',
          '关键词提取',
          '模糊匹配',
          '相关性评分'
        ]
      };
    } else {
      return {
        success: false,
        message: '无法获取统计信息',
        error: healthInfo.message
      };
    }
  } catch (error) {
    console.error('获取搜索统计失败:', error);
    return {
      success: false,
      message: '获取统计信息失败',
      error: error.message
    };
  }
}
