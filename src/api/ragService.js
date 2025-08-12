/**
 * RAG智能问答服务 - 调用新的RAG系统API
 */

const RAG_API_BASE_URL = 'http://localhost:8000/api/v1/rag';

/**
 * RAG智能问答
 * @param {string} query 用户查询
 * @param {number} maxResults 最大返回结果数
 * @param {boolean} includeSearchDetails 是否包含搜索详情
 * @returns {Promise<Object>} RAG响应结果
 */
export async function ragQuery(query, maxResults = 5, includeSearchDetails = false) {
  try {
    const response = await fetch(`${RAG_API_BASE_URL}/query`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ 
        query,
        max_results: maxResults,
        include_search_details: includeSearchDetails
      })
    });

    if (!response.ok) {
      throw new Error(`RAG查询失败: ${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    return {
      success: true,
      answer: result.answer,
      results: result.results || [],
      totalResults: result.total_results,
      processingTime: result.processing_time,
      queryExpanded: result.query_expanded,
      searchContext: result.search_context,
      timestamp: result.timestamp
    };
  } catch (error) {
    console.error('RAG问答失败:', error);
    return { 
      success: false,
      error: error.message,
      answer: '抱歉，智能问答服务暂时不可用，请稍后再试。',
      results: [],
      totalResults: 0
    };
  }
}

/**
 * RAG混合搜索
 * @param {string} query 搜索查询
 * @param {number} limit 结果数量限制
 * @returns {Promise<Object>} 搜索结果
 */
export async function ragSearch(query, limit = 600) {
  try {
    const response = await fetch(`${RAG_API_BASE_URL}/search`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ 
        query,
        limit
      })
    });

    if (!response.ok) {
      throw new Error(`RAG搜索失败: ${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    return {
      success: true,
      results: result.results || [],
      total: result.total,
      query: result.query,
      expandedQuery: result.expanded_query
    };
  } catch (error) {
    console.error('RAG搜索失败:', error);
    return { 
      success: false,
      error: error.message,
      results: [],
      total: 0
    };
  }
}

/**
 * 获取查询建议
 * @param {string} prefix 查询前缀
 * @param {number} limit 建议数量
 * @returns {Promise<Object>} 建议结果
 */
export async function getQuerySuggestions(prefix, limit = 5) {
  try {
    const response = await fetch(`${RAG_API_BASE_URL}/suggest?q=${encodeURIComponent(prefix)}&limit=${limit}`, {
      method: 'GET',
      headers: { 
        'Accept': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`获取建议失败: ${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    return {
      success: true,
      suggestions: result.suggestions || [],
      query: result.query
    };
  } catch (error) {
    console.error('获取查询建议失败:', error);
    return { 
      success: false,
      error: error.message,
      suggestions: []
    };
  }
}

/**
 * 检查RAG服务健康状态
 * @returns {Promise<boolean>} 服务是否可用
 */
export async function checkRagServiceHealth() {
  try {
    const response = await fetch(`${RAG_API_BASE_URL}/health`, {
      method: 'GET',
      headers: { 
        'Accept': 'application/json'
      },
      timeout: 5000
    });

    if (!response.ok) {
      return false;
    }

    const result = await response.json();
    return result.status === 'healthy';
  } catch (error) {
    console.error('RAG服务健康检查失败:', error);
    return false;
  }
}

/**
 * 提交用户反馈
 * @param {string} query 原始查询
 * @param {number} answerQuality 回答质量评分 (1-5)
 * @param {boolean} isHelpful 是否有帮助
 * @param {string} comment 额外评论
 * @returns {Promise<Object>} 反馈结果
 */
export async function submitFeedback(query, answerQuality, isHelpful, comment = '') {
  try {
    const response = await fetch(`${RAG_API_BASE_URL}/feedback`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ 
        query,
        answer_quality: answerQuality,
        is_helpful: isHelpful,
        comment
      })
    });

    if (!response.ok) {
      throw new Error(`提交反馈失败: ${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    return {
      success: true,
      message: result.message,
      feedbackId: result.feedback_id
    };
  } catch (error) {
    console.error('提交反馈失败:', error);
    return { 
      success: false,
      error: error.message,
      message: '反馈提交失败，请稍后再试。'
    };
  }
}