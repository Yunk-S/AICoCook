/**
 * AI Meal Coach 服务
 * 调用 AI-Meal-Coach 后端 (FastAPI) 的 API
 */

// 直连后端API，不使用代理
const API_BASE_URL = 'http://localhost:8000/api/v1';

// 添加调试日志
console.log('[aiMealCoachService] 模块加载完成');

/**
 * 从 sessionStorage 获取 AI 服务商和 API 密钥
 * @returns {{provider: string, apiKey: string}}
 */
function getApiCredentials() {
  const provider = sessionStorage.getItem('ai_provider') || 'google';
  const apiKey = sessionStorage.getItem('api_key') || '';
  return { provider, apiKey };
}

/**
 * 流式聊天服务 - 解决超时问题，提升用户体验
 * @param {string} message 用户消息
 * @param {function} onChunk 收到数据块时的回调
 * @param {function} onDone 完成时的回调
 * @param {function} onError 错误时的回调
 * @returns {Promise<void>}
 */
const streamChatWithCoach = async (message, onChunk, onDone, onError) => {
  const { provider, apiKey } = getApiCredentials();

  if (!apiKey) {
    const error = new Error('请先配置API密钥');
    if (onError) onError(error);
    throw error;
  }

  try {
    console.log('[streamChatWithCoach] 开始流式聊天', { provider, messageLength: message.length });

    const response = await fetch(`${API_BASE_URL}/ai/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Provider': provider,
        'X-API-Key': apiKey,
      },
      body: JSON.stringify({ 
        messages: [{ role: 'user', content: message }],
        temperature: 0.7,
        stream: true
      }),
    });

    if (!response.ok) {
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch (e) {
        // 忽略JSON解析错误
      }
      throw new Error(errorMessage);
    }

    // 创建读取器处理流式数据
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    console.log('[streamChatWithCoach] 开始读取流式数据');

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        console.log('[streamChatWithCoach] 流式数据读取完成');
        break;
      }
      
      // 解码数据块
      buffer += decoder.decode(value, { stream: true });
      
      // 处理完整的SSE消息
      const lines = buffer.split('\n');
      buffer = lines.pop(); // 保留不完整的行
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            
            console.log('[streamChatWithCoach] 收到数据块:', data.type);
            
            switch (data.type) {
              case 'start':
                console.log('[streamChatWithCoach] 开始接收', data.provider);
                break;
              case 'chunk':
                if (onChunk) onChunk(data);
                break;
              case 'done':
                console.log('[streamChatWithCoach] 接收完成');
                if (onDone) onDone(data);
                return data;
              case 'error':
                console.error('[streamChatWithCoach] 服务器错误:', data.content);
                const serverError = new Error(data.content);
                if (onError) onError(serverError);
                throw serverError;
            }
          } catch (e) {
            console.warn('[streamChatWithCoach] 解析SSE数据失败:', line, e);
          }
        }
      }
    }
  } catch (error) {
    console.error('[streamChatWithCoach] 流式聊天错误:', error);
    if (onError) onError(error);
    throw error;
  }
};

/**
 * 与 AI 助手进行聊天
 * @param {Array<{role: string, content: string}>} messages 对话消息历史
 * @returns {Promise<Object>} 返回 AI 的回复
 */
const chatWithCoach = async (messages) => {
  const { provider, apiKey } = getApiCredentials();

  if (!apiKey) {
    const errorMsg = `请在设置中提供 ${provider} 的 API 密钥。`;
    console.error(errorMsg);
    alert(errorMsg);
    throw new Error(errorMsg);
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30秒超时

    const response = await fetch(`${API_BASE_URL}/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Provider': provider,
        'X-API-Key': apiKey,
      },
      body: JSON.stringify({
        messages: messages,
        temperature: 0.7,
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorMessage = `AI 服务请求失败: ${response.status}`;
      try {
        const errData = await response.json();
        // 适配后端错误格式
        const errorDetail = errData.error?.message || errData.detail || errData.message || '未知错误';
        errorMessage += ` - ${errorDetail}`;
      } catch (parseError) {
        errorMessage += ' - 无法解析错误详情';
      }
      
      // 根据状态码提供更具体的错误信息
      if (response.status === 401) {
        errorMessage = '请检查您的 API 密钥是否正确';
      } else if (response.status === 429) {
        errorMessage = 'API 请求频率过高，请稍后再试';
      } else if (response.status >= 500) {
        errorMessage = 'AI 服务暂时不可用，请稍后再试';
      }
      
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('AI 聊天服务调用失败:', error);
    
    // 处理不同类型的错误
    if (error.name === 'AbortError') {
      throw new Error('请求超时，请检查网络连接或稍后再试');
    } else if (error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查 AI 后端服务是否正常运行');
    }
    
    throw error;
  }
}

/**
 * 检查 AI Coach 服务的健康状态
 * @returns {Promise<boolean>}
 */
async function checkCoachApiHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) return false;
    const data = await response.json();
    return data.status === 'ok';
  } catch (error) {
    console.error('检查 AI Coach API 健康状态失败:', error);
    return false;
  }
};

// 导出所有函数
export { chatWithCoach, streamChatWithCoach, checkCoachApiHealth };
