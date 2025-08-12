/**
 * 修复版菜谱搜索服务
 * 专门解决前后端信息传输格式问题
 * 包含后备搜索机制
 */
import { fallbackSearch, generateSearchSuggestions } from './fallbackSearchService.js';

// 直连后端搜索引擎，绕过Vite代理
const API_BASE_URL = 'http://localhost:8080';

/**
 * 直接的搜索API调用 - 无复杂处理
 * @param {string} query 搜索关键词
 * @param {number} limit 结果数量限制
 * @returns {Promise<Object>} 搜索结果
 */
export async function directSearchRecipes(query, limit = 600) {
  console.log('🔍 [FIXED] 开始直接搜索:', query);
  
  // 基础验证
  if (!query || typeof query !== 'string' || !query.trim()) {
    throw new Error('搜索关键词不能为空');
  }
  
  const requestData = {
    query: query.trim(),
    limit: Math.min(Math.max(1, limit), 600)
  };
  
  console.log('📤 [FIXED] 发送请求数据:', requestData);
  
  try {
    // 1. 发送请求
    const response = await fetch(`${API_BASE_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json',
        'Connection': 'keep-alive'
      },
      body: JSON.stringify(requestData),
      timeout: 30000 // 30秒超时
    });
    
    console.log('📊 [FIXED] 响应状态:', response.status, response.statusText);
    console.log('📊 [FIXED] 响应URL:', response.url);
    
    // 2. 检查响应状态
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorText = await response.text();
        if (errorText) {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.error || errorData.message || errorText;
        }
      } catch (e) {
        // 如果无法解析错误响应，使用默认错误信息
      }
      throw new Error(errorMessage);
    }
    
    // 3. 获取响应数据
    const responseText = await response.text();
    console.log('📄 [FIXED] 原始响应文本:', responseText);
    
    if (!responseText) {
      throw new Error('服务器返回空响应');
    }
    
    // 4. 解析JSON
    let backendResult;
    try {
      backendResult = JSON.parse(responseText);
      console.log('✅ [FIXED] JSON解析成功:', backendResult);
    } catch (parseError) {
      console.error('❌ [FIXED] JSON解析失败:', parseError.message);
      console.error('📄 [FIXED] 无法解析的文本:', responseText);
      throw new Error(`响应数据格式错误: ${parseError.message}`);
    }
    
    // 5. 验证后端响应格式
    if (backendResult.error) {
      throw new Error(backendResult.error);
    }
    
    if (!backendResult.hasOwnProperty('results')) {
      console.error('❌ [FIXED] 响应缺少results字段:', backendResult);
      throw new Error('后端响应格式错误：缺少results字段');
    }
    
    if (!Array.isArray(backendResult.results)) {
      console.error('❌ [FIXED] results字段不是数组:', typeof backendResult.results, backendResult.results);
      throw new Error('后端响应格式错误：results字段不是数组');
    }
    
    // 6. 格式化返回结果
    const result = {
      success: true,
      recipes: backendResult.results,
      totalResults: backendResult.total || backendResult.results.length,
      query: backendResult.query || query.trim(),
      message: `找到 ${backendResult.total || backendResult.results.length} 个相关菜谱`,
      analysis: {
        searchType: '关键词搜索',
        searchTime: Date.now(),
        backendResponse: backendResult
      },
      error: null,
      timestamp: new Date().toISOString()
    };
    
    console.log('🎯 [FIXED] 最终返回结果:', result);
    return result;
    
  } catch (error) {
    console.error('❌ [FIXED] 后端搜索失败，尝试前端后备搜索:', error);
    
    // 使用前端后备搜索
    try {
      const fallbackResult = await fallbackSearch(query, limit);
      console.log('🔄 [FIXED] 使用前端后备搜索结果:', fallbackResult);
      return fallbackResult;
    } catch (fallbackError) {
      console.error('❌ [FIXED] 前端后备搜索也失败:', fallbackError);
      
      // 返回标准化错误格式
      return {
        success: false,
        recipes: [],
        totalResults: 0,
        query: query.trim(),
        message: `搜索失败: ${error.message}，后备搜索也失败: ${fallbackError.message}`,
        analysis: null,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }
}

/**
 * 健康检查 - 直接版本
 * @returns {Promise<Object>} 健康状态
 */
export async function directHealthCheck() {
  console.log('🏥 [FIXED] 开始健康检查');
  
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Connection': 'keep-alive'
      },
      timeout: 30000 // 30秒超时
    });
    
    console.log('📊 [FIXED] 健康检查响应:', response.status, response.statusText);
    
    if (!response.ok) {
      throw new Error(`健康检查失败: HTTP ${response.status}`);
    }
    
    const result = await response.json();
    console.log('✅ [FIXED] 健康检查成功:', result);
    
    return {
      isHealthy: true,
      healthy: true,
      status: result.status || 'healthy',
      message: result.message || '服务正常',
      details: result
    };
    
  } catch (error) {
    console.error('❌ [FIXED] 健康检查失败:', error);
    
    return {
      isHealthy: false,
      healthy: false,
      status: 'error',
      message: error.message,
      error: error.message
    };
  }
}

/**
 * 测试特定关键词的搜索功能
 * @param {string} keyword 测试关键词
 * @returns {Promise<Object>} 测试结果
 */
export async function testKeywordSearch(keyword) {
  console.log(`🧪 [FIXED] 测试关键词搜索: "${keyword}"`);
  
  try {
    const result = await directSearchRecipes(keyword, 5);
    
    const testResult = {
      keyword: keyword,
      success: result.success,
      found: result.totalResults > 0,
      count: result.totalResults,
      firstResult: result.recipes.length > 0 ? result.recipes[0] : null,
      error: result.error,
      timestamp: new Date().toISOString()
    };
    
    console.log(`🎯 [FIXED] 测试结果:`, testResult);
    return testResult;
    
  } catch (error) {
    console.error(`❌ [FIXED] 测试失败:`, error);
    return {
      keyword: keyword,
      success: false,
      found: false,
      count: 0,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
}

/**
 * 批量测试多个关键词
 * @param {Array<string>} keywords 关键词列表
 * @returns {Promise<Array>} 测试结果列表
 */
export async function batchTestKeywords(keywords = ['土豆', '牛肉', '鸡蛋', '番茄', 'beef']) {
  console.log('🔄 [FIXED] 开始批量测试关键词:', keywords);
  
  const results = [];
  
  for (const keyword of keywords) {
    const result = await testKeywordSearch(keyword);
    results.push(result);
    
    // 间隔500ms避免过于频繁的请求
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  
  console.log('✅ [FIXED] 批量测试完成:', results);
  return results;
}

/**
 * 全面诊断搜索功能
 * @returns {Promise<Object>} 诊断报告
 */
export async function diagnosiseSearchFunction() {
  console.log('🔬 [FIXED] 开始全面诊断搜索功能');
  
  const diagnosis = {
    timestamp: new Date().toISOString(),
    backendHealth: null,
    searchTests: [],
    summary: {
      backendAvailable: false,
      searchWorking: false,
      chineseWorking: false,
      englishWorking: false,
      totalTests: 0,
      passedTests: 0
    }
  };
  
  try {
    // 1. 健康检查
    console.log('🏥 [FIXED] 步骤1: 健康检查');
    diagnosis.backendHealth = await directHealthCheck();
    diagnosis.summary.backendAvailable = diagnosis.backendHealth.isHealthy;
    
    if (!diagnosis.summary.backendAvailable) {
      console.log('❌ [FIXED] 后端不可用，跳过搜索测试');
      return diagnosis;
    }
    
    // 2. 搜索测试
    console.log('🔍 [FIXED] 步骤2: 搜索功能测试');
    const testKeywords = ['土豆', '牛肉', 'beef', 'potato'];
    diagnosis.searchTests = await batchTestKeywords(testKeywords);
    
    // 3. 统计结果
    diagnosis.summary.totalTests = diagnosis.searchTests.length;
    diagnosis.summary.passedTests = diagnosis.searchTests.filter(t => t.success).length;
    diagnosis.summary.searchWorking = diagnosis.summary.passedTests > 0;
    diagnosis.summary.chineseWorking = diagnosis.searchTests.filter(t => /[\u4e00-\u9fa5]/.test(t.keyword) && t.success).length > 0;
    diagnosis.summary.englishWorking = diagnosis.searchTests.filter(t => /^[a-zA-Z]+$/.test(t.keyword) && t.success).length > 0;
    
    console.log('📊 [FIXED] 诊断完成:', diagnosis.summary);
    return diagnosis;
    
  } catch (error) {
    console.error('❌ [FIXED] 诊断过程出错:', error);
    diagnosis.error = error.message;
    return diagnosis;
  }
}