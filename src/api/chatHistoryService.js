/**
 * 聊天历史记录存储服务
 * 使用localStorage存储聊天记录，支持导出到文件
 */

// 存储键名
const STORAGE_KEY = 'ai_chat_history';

/**
 * 获取初始化的聊天历史数据
 */
function getInitialChatHistory() {
  return {
    sessions: [],
    lastSessionId: null,
    createdAt: new Date().toISOString()
  };
}

/**
 * 读取聊天历史记录
 */
export function loadChatHistory() {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    if (data) {
      return JSON.parse(data);
    }
    // 如果localStorage中没有数据，返回初始数据
    const initialData = getInitialChatHistory();
    saveChatHistory(initialData);
    return initialData;
  } catch (error) {
    console.error('加载聊天历史失败:', error);
    return getInitialChatHistory();
  }
}

/**
 * 保存聊天历史记录
 */
export function saveChatHistory(historyData) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(historyData));
    // 同时触发导出到文件的操作
    exportChatHistoryToFile(historyData);
    return true;
  } catch (error) {
    console.error('保存聊天历史失败:', error);
    return false;
  }
}

/**
 * 创建新的聊天会话
 */
export function createChatSession() {
  try {
    const history = loadChatHistory();
    const sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const newSession = {
      id: sessionId,
      title: '新对话',
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    history.sessions.unshift(newSession); // 新会话放在最前面
    history.lastSessionId = sessionId;
    
    saveChatHistory(history);
    return sessionId;
  } catch (error) {
    console.error('创建聊天会话失败:', error);
    return null;
  }
}

/**
 * 更新聊天会话
 */
export function updateChatSession(sessionId, messages, title = null) {
  try {
    const history = loadChatHistory();
    const sessionIndex = history.sessions.findIndex(s => s.id === sessionId);
    
    if (sessionIndex === -1) {
      // 会话不存在，创建新会话
      const newSession = {
        id: sessionId,
        title: title || generateTitleFromFirstMessage(messages),
        messages: messages,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      history.sessions.unshift(newSession);
    } else {
      // 更新现有会话
      history.sessions[sessionIndex].messages = messages;
      history.sessions[sessionIndex].updatedAt = new Date().toISOString();
      
      if (title) {
        history.sessions[sessionIndex].title = title;
      } else if (!history.sessions[sessionIndex].title || history.sessions[sessionIndex].title === '新对话') {
        // 如果还没有标题，根据第一条用户消息生成标题
        history.sessions[sessionIndex].title = generateTitleFromFirstMessage(messages);
      }
      
      // 将更新的会话移到最前面
      const updatedSession = history.sessions.splice(sessionIndex, 1)[0];
      history.sessions.unshift(updatedSession);
    }
    
    history.lastSessionId = sessionId;
    saveChatHistory(history);
    return true;
  } catch (error) {
    console.error('更新聊天会话失败:', error);
    return false;
  }
}

/**
 * 获取特定聊天会话
 */
export function getChatSession(sessionId) {
  try {
    const history = loadChatHistory();
    return history.sessions.find(s => s.id === sessionId) || null;
  } catch (error) {
    console.error('获取聊天会话失败:', error);
    return null;
  }
}

/**
 * 获取最后一个聊天会话
 */
export function getLastChatSession() {
  try {
    const history = loadChatHistory();
    if (history.lastSessionId) {
      return getChatSession(history.lastSessionId);
    }
    return history.sessions.length > 0 ? history.sessions[0] : null;
  } catch (error) {
    console.error('获取最后聊天会话失败:', error);
    return null;
  }
}

/**
 * 删除聊天会话
 */
export function deleteChatSession(sessionId) {
  try {
    const history = loadChatHistory();
    const sessionIndex = history.sessions.findIndex(s => s.id === sessionId);
    
    if (sessionIndex !== -1) {
      history.sessions.splice(sessionIndex, 1);
      
      // 如果删除的是最后使用的会话，更新lastSessionId
      if (history.lastSessionId === sessionId) {
        history.lastSessionId = history.sessions.length > 0 ? history.sessions[0].id : null;
      }
      
      saveChatHistory(history);
      return true;
    }
    return false;
  } catch (error) {
    console.error('删除聊天会话失败:', error);
    return false;
  }
}

/**
 * 清空所有聊天历史
 */
export function clearAllChatHistory() {
  try {
    const emptyHistory = getInitialChatHistory();
    saveChatHistory(emptyHistory);
    return true;
  } catch (error) {
    console.error('清空聊天历史失败:', error);
    return false;
  }
}

/**
 * 根据第一条用户消息生成标题
 */
function generateTitleFromFirstMessage(messages) {
  const userMessage = messages.find(m => m.role === 'user');
  if (userMessage && userMessage.content) {
    let title = userMessage.content.trim();
    // 限制标题长度
    if (title.length > 30) {
      title = title.substring(0, 30) + '...';
    }
    return title;
  }
  return '新对话';
}

/**
 * 获取聊天会话列表（用于历史记录显示）
 */
export function getChatSessionList() {
  try {
    const history = loadChatHistory();
    return history.sessions.map(session => ({
      id: session.id,
      title: session.title,
      createdAt: session.createdAt,
      updatedAt: session.updatedAt,
      messageCount: session.messages.length
    }));
  } catch (error) {
    console.error('获取聊天会话列表失败:', error);
    return [];
  }
}

/**
 * 导出聊天历史到文件
 */
export function exportChatHistoryToFile(historyData) {
  try {
    // 创建一个Blob对象
    const dataStr = JSON.stringify(historyData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    
    // 创建一个临时的下载链接（如果需要手动下载）
    const url = URL.createObjectURL(blob);
    
    // 可以在控制台输出文件内容供调试
    console.log('聊天历史已更新:', historyData);
    
    // 清理URL对象
    setTimeout(() => URL.revokeObjectURL(url), 100);
    
    return url;
  } catch (error) {
    console.error('导出聊天历史失败:', error);
    return null;
  }
}

/**
 * 手动下载聊天历史文件
 */
export function downloadChatHistory() {
  try {
    const history = loadChatHistory();
    const dataStr = JSON.stringify(history, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    // 创建下载链接
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat_history_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    // 清理URL对象
    URL.revokeObjectURL(url);
    
    return true;
  } catch (error) {
    console.error('下载聊天历史失败:', error);
    return false;
  }
}

/**
 * 从文件导入聊天历史
 */
export function importChatHistoryFromFile(file) {
  return new Promise((resolve, reject) => {
    try {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const importedData = JSON.parse(e.target.result);
          
          // 验证数据格式
          if (importedData && Array.isArray(importedData.sessions)) {
            saveChatHistory(importedData);
            resolve(importedData);
          } else {
            reject(new Error('无效的聊天历史文件格式'));
          }
        } catch (parseError) {
          reject(new Error('文件解析失败: ' + parseError.message));
        }
      };
      reader.onerror = () => reject(new Error('文件读取失败'));
      reader.readAsText(file);
    } catch (error) {
      reject(error);
    }
  });
}

/**
 * 初始化聊天历史服务
 * 在页面加载时检查是否有已保存的历史记录
 */
export function initializeChatHistory() {
  try {
    const history = loadChatHistory();
    console.log('聊天历史已初始化，包含', history.sessions.length, '个会话');
    return history;
  } catch (error) {
    console.error('初始化聊天历史失败:', error);
    return getInitialChatHistory();
  }
}