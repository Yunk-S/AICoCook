<template>
  <div class="ai-coach-page">
    <!-- 背景层：与Home页面一致的紫色光晕 -->
    <div class="hero-background">
      <div class="radial-gradient"></div>
      <div class="purple-glow"></div>
    </div>

    <!-- 动画浮动blob背景 -->
    <div class="animated-blobs">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>  
      <div class="blob blob-3"></div>
    </div>

    <!-- 鼠标追踪光晕 -->
    <div class="mouse-glow" ref="mouseGlow"></div>

    <!-- 主容器 -->
    <div class="chat-hero-container">
      <!-- 标题区域 -->
      <div class="hero-header">
        <h1 class="gradient-title">{{ $t('aiCoach.title') }}</h1>
        <div class="title-divider"></div>
        <p class="hero-subtitle">{{ $t('aiCoach.subtitle') }}</p>
      </div>

      <!-- 聊天历史侧边栏 - 绝对定位，不影响主布局 -->
      <transition name="slide-left">
        <div v-if="showHistoryPanel" class="history-sidebar">
                      <div class="history-header">
              <h3>{{ $t('aiCoach.chatHistory') }}</h3>
              <div class="history-actions">
                <button class="history-action-btn" @click="clearAllHistory">
                  {{ $t('aiCoach.clearHistory') }}
                </button>
                <button class="history-action-btn" @click="startNewChatSession">
                  {{ $t('aiCoach.newChat') }}
                </button>
                <button class="history-action-btn close-btn" @click="showHistoryPanel = false">
                  <el-icon><Refresh /></el-icon>
                </button>
              </div>
            </div>
            
            <div class="history-list">
              <div v-if="sessionList.length === 0" class="empty-history">
                {{ $t('aiCoach.noHistory') }}
              </div>
            <div 
              v-for="session in sessionList" 
              :key="session.id"
              :class="['history-item', { active: session.id === currentSessionId }]"
              @click="loadChatSession(session.id)"
            >
              <div class="session-info">
                <div class="session-title">{{ session.title }}</div>
                                  <div class="session-meta">
                    {{ formatChatHistoryDate(session.updatedAt) }} • {{ session.messageCount }} {{ $t('aiCoach.messages') }}
                  </div>
              </div>
              <el-button 
                size="small" 
                type="danger" 
                text
                @click.stop="deleteSession(session.id)"
                class="delete-btn"
                              >
                  {{ $t('aiCoach.delete') }}
                </el-button>
            </div>
          </div>
        </div>
      </transition>

      <!-- 聊天输入卡片 - 固定居中 -->
      <div class="chat-input-card" ref="chatCard">
        <div class="chat-messages" ref="chatBox" v-if="messages.length > 1">
          <transition-group name="message" tag="div">
            <div v-for="(message, index) in messages" :key="`msg-${index}`" class="message-row" :class="message.role">
              <template v-if="message.role === 'user'">
                <div class="message-bubble" :class="[message.role, { 'streaming': message.isStreaming }]">
                  <div class="message-content" v-html="formatMessage(message.content)"></div>
                  
                  <!-- 流式响应指示器 -->
                  <div v-if="message.isStreaming" class="streaming-indicator">
                    <span class="streaming-cursor">|</span>
                    <span class="streaming-text">正在输入...</span>
                  </div>
                  
                  <div class="message-time">
                    {{ formatTime(new Date()) }}
                    <span v-if="message.model" class="model-info"> • {{ message.model }}</span>
                  </div>
                </div>
                <div class="avatar-wrapper" :class="message.role">
                  <div class="avatar" :class="message.role">
                    <el-icon><User /></el-icon>
                  </div>
                  <div class="avatar-glow" :class="message.role"></div>
                </div>
              </template>
              <template v-else>
                <div class="avatar-wrapper" :class="message.role">
                  <div class="avatar" :class="[message.role, { 'ai-thinking': isLoading && index === messages.length - 1 }]">
                    <el-icon>🤖</el-icon>
                  </div>
                  <div class="avatar-glow" :class="message.role"></div>
                </div>
                <div class="message-bubble" :class="[message.role, { 'streaming': message.isStreaming }]">
                  <div class="message-content" v-html="formatMessage(message.content)"></div>
                  
                  <!-- 流式响应指示器 -->
                  <div v-if="message.isStreaming" class="streaming-indicator">
                    <span class="streaming-cursor">|</span>
                    <span class="streaming-text">正在输入...</span>
                  </div>
                  
                  <div class="message-time">
                    {{ formatTime(new Date()) }}
                    <span v-if="message.model" class="model-info"> • {{ message.model }}</span>
                  </div>
                </div>
              </template>
            </div>
          </transition-group>
          
          <div v-if="isLoading" class="message-row assistant loading" key="loading">
            <div class="avatar-wrapper assistant">
              <div class="avatar assistant typing">
                <el-icon class="typing-icon">🤖</el-icon>
              </div>
              <div class="avatar-glow assistant"></div>
            </div>
            <div class="message-bubble assistant">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <div class="message-time">{{ $t('aiCoach.thinking') }}</div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="input-section">
          <textarea 
            v-model="userInput"
            class="chat-textarea"
            :placeholder="$t('aiCoach.placeholder')"
            @keydown.enter.prevent="sendMessage"
            @focus="isInputFocused = true"
            @blur="isInputFocused = false"
            :disabled="isLoading"
            rows="3"
          ></textarea>
          
                      <div class="input-actions">
              <div class="action-buttons">
                <button 
                  class="action-btn" 
                  @click="showHistoryPanel = !showHistoryPanel"
                  :title="$t('aiCoach.chatHistory')"
                >
                  <el-icon><DocumentAdd /></el-icon>
                </button>
                <button class="action-btn" @click="settingsDialogVisible = true">
                  <el-icon><Setting /></el-icon>
                </button>
            </div>
            
            <button 
              class="send-button"
              @click="sendMessage" 
              :disabled="isLoading || !userInput.trim()"
              :class="{ 'enabled': userInput.trim() && !isLoading }"
            >
              <el-icon v-if="!isLoading"><Promotion /></el-icon>
              <span v-if="!isLoading">{{ $t('aiCoach.send') }}</span>
              <div v-else class="loading-spinner"></div>
            </button>
          </div>
        </div>
      </div>

      <!-- 服务状态显示区域 -->
      <div class="service-status-section">
        <div class="status-indicators">
          <el-tooltip :content="ragStatus.message" placement="top">
            <div class="status-indicator" :class="`status-${ragStatus.status}`">
              <span class="status-icon">🗄️</span>
              <span class="status-text">RAG</span>
            </div>
          </el-tooltip>
          <el-tooltip :content="llmStatus.message" placement="top">
            <div class="status-indicator" :class="`status-${llmStatus.status}`">
              <span class="status-icon">🤖</span>
              <span class="status-text">LLM</span>
            </div>
          </el-tooltip>
        </div>
      </div>

      <!-- 快捷建议 -->
      <div class="quick-suggestions" v-if="messages.length <= 1">
        <div class="suggestion-label">💡 {{ $t('aiCoach.suggestionLabel') }}</div>
        <div class="suggestions">
          <button 
            v-for="suggestion in quickSuggestions" 
            :key="suggestion"
            @click="handleSuggestionClick(suggestion)"
            class="suggestion-btn"
          >
            {{ suggestion }}
          </button>
        </div>
      </div>
    </div>


    <el-dialog 
      v-model="settingsDialogVisible" 
      :title="$t('aiCoach.settingsTitle')" 
      width="50%"
      class="api-settings-dialog">
      <div class="settings-content">
        <div class="config-guide-card">
          <h4>{{ $t('aiCoach.configTitle') }}</h4>
          <p>{{ $t('aiCoach.configDescription') }}</p>
        </div>
        
        <el-form label-position="top">
          <el-form-item :label="$t('aiCoach.providerLabel')">
            <el-select v-model="apiProvider" :placeholder="$t('aiCoach.providerPlaceholder')" style="width: 100%">
              <el-option label="Google Gemini" value="google">
                <span>Google Gemini</span>
                <span class="option-tag">{{ $t('aiCoach.recommended') }}</span>
              </el-option>
              <el-option label="OpenAI" value="openai">
                <span>OpenAI GPT</span>
                <span class="option-tag">{{ $t('aiCoach.popular') }}</span>
              </el-option>
              <el-option label="豆包 (DouBao)" value="doubao">
                <span>豆包 AI</span>
                <span class="option-tag">{{ $t('aiCoach.domestic') }}</span>
              </el-option>
              <el-option label="智谱 (ZhiPu)" value="zhipu">
                <span>智谱 GLM</span>
                <span class="option-tag">{{ $t('aiCoach.domestic') }}</span>
              </el-option>
              <el-option label="DeepSeek" value="deepseek">
                <span>DeepSeek</span>
                <span class="option-tag">{{ $t('aiCoach.economical') }}</span>
              </el-option>
              <el-option label="DeepSeek R1" value="deepseek-r1">
                <span>DeepSeek R1</span>
                <span class="option-tag">{{ $t('aiCoach.reasoning') }}</span>
              </el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item :label="$t('aiCoach.apiKeyLabel')">
            <el-input 
              v-model="apiKey" 
              show-password 
              :placeholder="$t('aiCoach.apiKeyPlaceholder')"
              style="width: 100%">
            </el-input>
            <div class="api-hint-text">
              <div v-if="apiProvider === 'google'">
                💡 {{ $t('aiCoach.googleApiHint') }}: <a href="https://ai.google.dev/" target="_blank">Google AI Studio</a>
                <br><span class="support-text">🧠 {{ $t('aiCoach.supportsVectorGeneration') }}</span>
              </div>
              <div v-if="apiProvider === 'openai'">
                💡 Get API Key: <a href="https://platform.openai.com/api-keys" target="_blank">OpenAI API Keys</a>
                <br><span class="support-text">🧠 {{ $t('aiCoach.supportsVectorGeneration') }}</span>
              </div>
              <div v-if="apiProvider === 'doubao'">
                💡 Get API Key: <a href="https://console.volcengine.com/ark/" target="_blank">Volcano Engine DouBao</a>
                <br><span class="warning-text">⚠️ {{ $t('aiCoach.vectorGenerationRestricted') }}</span>
              </div>
              <div v-if="apiProvider === 'zhipu'">
                💡 Get API Key: <a href="https://open.bigmodel.cn/" target="_blank">ZhiPu AI Platform</a>
                <br><span class="support-text">🧠 {{ $t('aiCoach.supportsVectorGeneration') }}</span>
              </div>
              <div v-if="apiProvider === 'deepseek'">
                💡 {{ $t('aiCoach.deepseekApiHint') }}: <a href="https://platform.deepseek.com/" target="_blank">{{ $t('aiCoach.deepseekPlatform') }}</a>
                <br><span class="warning-text">⚠️ {{ $t('aiCoach.vectorGenerationRestricted') }}</span>
              </div>
              <div v-if="apiProvider === 'deepseek-r1'">
                💡 {{ $t('aiCoach.deepSeekSameKey') }}: <a href="https://platform.deepseek.com/" target="_blank">{{ $t('aiCoach.deepseekPlatform') }}</a>
                <br><span class="info-text">🧠 {{ $t('aiCoach.reasoning') }} - R1 specializes in logic reasoning and math</span>
                <br><span class="warning-text">⚠️ {{ $t('aiCoach.vectorGenerationRestricted') }}</span>
              </div>
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-alert 
              v-if="!apiKey" 
              :title="$t('aiCoach.apiKeyRequired')" 
              type="warning" 
              :closable="false">
            </el-alert>
            <el-alert 
              v-if="apiKey" 
              :title="$t('aiCoach.apiKeySet')" 
              type="success" 
              :closable="false">
              <template #default>
                {{ $t('aiCoach.apiKeySecurity') }}
              </template>
            </el-alert>
          </el-form-item>
        </el-form>
        
                <!-- RAG数据库信息 -->
        <el-divider content-position="left">
                     <span class="rag-section-title">🗄️ {{ $t('aiCoach.ragDatabaseInfo') }}</span>
        </el-divider>
        
        <div class="rag-info-section">
          <el-row :gutter="16" style="margin-bottom: 16px;">
            <el-col :span="12">
              <el-statistic :title="$t('aiCoach.vectorCount')" :value="ragInfo.vectorCount" />
            </el-col>
            <el-col :span="12">
              <el-statistic :title="$t('aiCoach.fileCount')" :value="ragInfo.fileCount" />
            </el-col>
          </el-row>
          
          <!-- 向量生成提示和按钮 -->
          <div v-if="ragInfo.vectorCount === 0" style="margin-bottom: 16px;">
            <el-alert 
              type="warning" 
              :title="$t('aiCoach.vectorDataMissing')" 
              :description="$t('aiCoach.vectorDataDescription')"
              show-icon 
              :closable="false">
              <template #default>
                <div style="margin-top: 12px;">
                  <button 
                    v-if="['google', 'openai', 'zhipu'].includes(apiProvider)" 
                    class="settings-btn generate-btn"
                    :disabled="isGeneratingVectors || !apiKey"
                    @click="generateVectors">
                    <el-icon v-if="!isGeneratingVectors"><DocumentAdd /></el-icon>
                    <span v-if="isGeneratingVectors">{{ $t('aiCoach.generatingVectorData') }}</span>
                    <span v-else>{{ $t('aiCoach.generateVectorData') }}</span>
                  </button>
                  <div v-else class="provider-switch-hint">
                    💡 {{ $t('aiCoach.switchToSupportedProviders') }}
                  </div>
                </div>
              </template>
            </el-alert>
          </div>
          
          <div class="file-list-section">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
              <span class="file-list-title">📄 {{ $t('aiCoach.importedFilesList') }}</span>
              <button class="settings-btn refresh-btn" @click="refreshRagInfo" :disabled="ragInfoLoading">
                <el-icon><Refresh /></el-icon> {{ $t('aiCoach.refresh') }}
              </button>
            </div>
            
            <el-scrollbar max-height="200px">
              <div v-if="ragInfo.files.length === 0" class="empty-files">
                <el-empty :description="$t('aiCoach.noImportedFiles')" :image-size="60" />
              </div>
              <div v-else class="file-list">
                <div v-for="file in ragInfo.files" :key="file.source" class="file-item">
                  <div class="file-info">
                    <span class="file-icon">{{ getFileIcon(file.source) }}</span>
                    <div class="file-details">
                      <div class="file-name">{{ file.source }}</div>
                      <div class="file-stats">
                        {{ file.count }} {{ $t('aiCoach.records') }} • {{ formatDate(file.lastImported) }}
                      </div>
                    </div>
                  </div>
                  <el-tag size="small" :type="file.count > 0 ? 'success' : 'info'">
                    {{ file.count }}
                  </el-tag>
                </div>
              </div>
            </el-scrollbar>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="settings-footer">
          <button class="settings-btn cancel-btn" @click="settingsDialogVisible = false">
            {{ $t('aiCoach.cancel') }}
          </button>
          <button 
            v-if="apiKey"
            class="settings-btn clear-btn"
            @click="clearApiKey">
            {{ $t('aiCoach.clearApiKey') }}
          </button>
          <button 
            class="settings-btn save-btn"
            @click="saveSettings"
            :disabled="!apiKey || !apiProvider">
            {{ $t('aiCoach.saveSettings') }}
          </button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { Setting, User, ChatLineRound, Promotion, Refresh, DocumentAdd } from '@element-plus/icons-vue';
import { chatWithCoach, streamChatWithCoach } from '../api/aiMealCoachService';
import { useI18n } from 'vue-i18n';
import { formatDate } from '../utils/helpers';
import { 
  loadChatHistory,
  saveChatHistory,
  createChatSession,
  updateChatSession,
  getLastChatSession,
  getChatSession,
  getChatSessionList,
  deleteChatSession,
  clearAllChatHistory,
  initializeChatHistory
} from '../api/chatHistoryService';

const { t, locale } = useI18n();

const messages = ref([]);
const userInput = ref('');
const isLoading = ref(false);
const chatBox = ref(null);
const settingsDialogVisible = ref(false);
const apiProvider = ref('google');
const apiKey = ref('');
const isInputFocused = ref(false);
const mouseGlow = ref(null);
const chatCard = ref(null);

// 聊天历史相关状态
const currentSessionId = ref(null);
const chatHistory = ref(null);
const showHistoryPanel = ref(false);
const sessionList = ref([]);

// 服务状态
const ragStatus = ref({
  status: 'unknown', // 'healthy', 'warning', 'error', 'unknown'
  message: 'Checking...'
});

const llmStatus = ref({
  status: 'unknown',
  message: 'Checking...'
});

// RAG数据库信息
const ragInfo = ref({
  vectorCount: 0,
  fileCount: 0,
  files: []
});

const ragInfoLoading = ref(false);
const isGeneratingVectors = ref(false);

// 响应式的建议和欢迎消息
const quickSuggestions = computed(() => [
  t('aiCoach.suggestions.weightLoss'),
  t('aiCoach.suggestions.healthyRecipes'),
  t('aiCoach.suggestions.diabetes'),
  t('aiCoach.suggestions.pregnancy'),
  t('aiCoach.suggestions.children')
]);

const welcomeMessage = computed(() => t('aiCoach.welcomeMessage'));

// 初始化欢迎消息
const initializeWelcomeMessage = () => {
  if (messages.value.length === 0 || messages.value[0].role === 'assistant') {
    messages.value = [
      { role: 'assistant', content: welcomeMessage.value }
    ];
  }
};

// 监听语言变化，更新欢迎消息
watch(locale, () => {
  if (messages.value.length > 0 && messages.value[0].role === 'assistant') {
          // 只更新第一条欢迎消息，保留用户的对话历史
      messages.value[0].content = welcomeMessage.value;
      saveCurrentSession();
  }
});

// 聊天历史相关方法
const saveCurrentSession = () => {
  if (currentSessionId.value && messages.value.length > 1) {
    const conversationMessages = messages.value.filter((msg, index) => {
      return msg.role === 'user' || (msg.role === 'assistant' && index > 0);
    });
    
    // 只有在存在用户消息和对应的AI回复时才保存会话
    const hasUserMessage = conversationMessages.some(msg => msg.role === 'user');
    const hasAiResponse = conversationMessages.some(msg => msg.role === 'assistant');
    
    if (conversationMessages.length > 0 && hasUserMessage && hasAiResponse) {
      updateChatSession(currentSessionId.value, conversationMessages);
      refreshSessionList();
    }
  }
};

const startNewSession = () => {
  currentSessionId.value = createChatSession();
  refreshSessionList();
  return currentSessionId.value;
};

const loadLastSession = () => {
  try {
    const lastSession = getLastChatSession();
    if (lastSession && lastSession.messages.length > 0) {
      currentSessionId.value = lastSession.id;
      const welcomeMsg = { role: 'assistant', content: welcomeMessage.value };
      messages.value = [welcomeMsg, ...lastSession.messages];
      
      nextTick(() => {
        scrollToBottom();
      });
      
      return true;
    }
  } catch (error) {
    console.error('加载历史会话失败:', error);
  }
  return false;
};

const refreshSessionList = () => {
  sessionList.value = getChatSessionList();
};

const loadChatSession = (sessionId) => {
  try {
    const session = getChatSession(sessionId);
    if (session) {
      saveCurrentSession();
      currentSessionId.value = sessionId;
      const welcomeMsg = { role: 'assistant', content: welcomeMessage.value };
      messages.value = [welcomeMsg, ...session.messages];
      showHistoryPanel.value = false;
      
      nextTick(() => {
        scrollToBottom();
      });
    }
  } catch (error) {
    console.error('加载聊天会话失败:', error);
    ElMessage.error(t('aiCoach.loadSessionFailed'));
  }
};

const startNewChatSession = () => {
  saveCurrentSession();
  const newSessionId = startNewSession();
  if (newSessionId) {
    initializeWelcomeMessage();
    showHistoryPanel.value = false;
    refreshSessionList();
    ElMessage.success(t('aiCoach.newChatCreated'));
  }
};

const deleteSession = (sessionId) => {
  if (deleteChatSession(sessionId)) {
    if (currentSessionId.value === sessionId) {
      startNewChatSession();
    }
    refreshSessionList();
    ElMessage.success(t('aiCoach.sessionDeleted'));
  } else {
    ElMessage.error(t('aiCoach.deleteSessionFailed'));
  }
};

const clearAllHistory = () => {
  if (clearAllChatHistory()) {
    startNewChatSession();
    refreshSessionList();
    ElMessage.success(t('aiCoach.allHistoryCleared'));
  } else {
    ElMessage.error(t('aiCoach.clearHistoryFailed'));
  }
};

const formatChatHistoryDate = (dateStr) => {
  const date = new Date(dateStr);
  const now = new Date();
  const diffInMs = now - date;
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
  
  if (diffInDays === 0) {
    return date.toLocaleTimeString(locale.value === 'zh' ? 'zh-CN' : 'en-US', { hour: '2-digit', minute: '2-digit' });
  } else if (diffInDays === 1) {
    return locale.value === 'zh' ? '昨天' : 'Yesterday';
  } else if (diffInDays < 7) {
    return locale.value === 'zh' ? `${diffInDays}天前` : `${diffInDays} days ago`;
  } else {
    return date.toLocaleDateString(locale.value === 'zh' ? 'zh-CN' : 'en-US', { month: 'short', day: 'numeric' });
  }
};

// 监听消息变化，实时保存
watch(messages, () => {
  // 防抖保存，避免频繁写入
  if (saveTimeout) {
    clearTimeout(saveTimeout);
  }
  saveTimeout = setTimeout(() => {
    saveCurrentSession();
  }, 1000); // 1秒后保存
}, { deep: true });

let saveTimeout = null;

onMounted(() => {
  // 初始化聊天历史服务
  chatHistory.value = initializeChatHistory();
  refreshSessionList();
  
  // 尝试加载上次的聊天会话
  const hasLoadedSession = loadLastSession();
  
  // 如果没有加载到历史会话，初始化欢迎消息
  if (!hasLoadedSession) {
    initializeWelcomeMessage();
    startNewSession();
  }
  
  // 🔒 安全增强：使用sessionStorage保存API密钥，关闭浏览器后自动清除
  // 页面刷新时可以保持API密钥，但关闭浏览器后会自动清除
  
  // 从sessionStorage读取API配置（仅在浏览器会话期间有效）
  const savedProvider = sessionStorage.getItem('ai_provider');
  const savedApiKey = sessionStorage.getItem('api_key');
  
  apiProvider.value = savedProvider || 'google';
  apiKey.value = savedApiKey || '';
  
  // 清除localStorage中的历史数据（防止持久化存储）
  localStorage.removeItem('api_key');
  localStorage.removeItem('ai_provider');
  
      // 监听浏览器关闭事件，确保数据清除
    window.addEventListener('beforeunload', () => {
      saveCurrentSession();
      sessionStorage.removeItem('api_key');
      sessionStorage.removeItem('ai_provider');
    });
    
    window.addEventListener('pagehide', () => {
      saveCurrentSession();
    });
    
    // 定期自动保存聊天历史（每30秒）
    setInterval(() => {
      saveCurrentSession();
    }, 30000);
  
  // 初始化服务状态检查
  checkServiceStatus();
  refreshRagInfo();
  
  // 定期检查服务状态（每30秒）
  setInterval(checkServiceStatus, 30000);

  // 初始化鼠标追踪光晕效果
  setupMouseGlow();
});

// 鼠标追踪光晕效果
const setupMouseGlow = () => {
  const handleMouseMove = (e) => {
    if (mouseGlow.value) {
      const { clientX, clientY } = e;
      mouseGlow.value.style.transform = `translate(${clientX - 400}px, ${clientY - 400}px)`;
    }
  };

  document.addEventListener('mousemove', handleMouseMove);
  
  // 清理事件监听器
  return () => {
    document.removeEventListener('mousemove', handleMouseMove);
  };
};

const scrollToBottom = () => {
  nextTick(() => {
    if (chatBox.value) {
      chatBox.value.scrollTop = chatBox.value.scrollHeight;
    }
  });
};

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;

  const userMessage = { role: 'user', content: userInput.value };
  messages.value.push(userMessage);
  
  const messageText = userInput.value;
  userInput.value = '';
  isLoading.value = true;
  scrollToBottom();

  // 创建流式响应消息占位符
  const responseMessageId = Date.now() + Math.random();
  const responseMessage = {
    id: responseMessageId,
    role: 'assistant',
    content: '',
    isStreaming: true
  };
  messages.value.push(responseMessage);

  try {
    // 优先使用流式聊天（解决超时问题）
    await streamChatWithCoach(
      messageText,
      // onChunk - 收到数据块时
      (chunkData) => {
        const messageIndex = messages.value.findIndex(m => m.id === responseMessageId);
        if (messageIndex !== -1) {
          // 累积更新内容，创造打字效果
          messages.value[messageIndex].content = chunkData.accumulated || (messages.value[messageIndex].content + chunkData.content);
          // 自动滚动到底部
          nextTick(() => scrollToBottom());
        }
      },
      // onDone - 完成时
      (finalData) => {
        const messageIndex = messages.value.findIndex(m => m.id === responseMessageId);
        if (messageIndex !== -1) {
          messages.value[messageIndex].content = finalData.content;
          messages.value[messageIndex].isStreaming = false;
          if (finalData.model) {
            messages.value[messageIndex].model = finalData.model;
          }
        }
        ElMessage.success(`响应完成 (${finalData.provider || 'AI'})`);
      },
      // onError - 错误时
      (error) => {
        console.warn('流式聊天错误，尝试普通模式:', error);
        // 流式失败时，尝试普通聊天作为回退
        fallbackToNormalChat(messageText, responseMessageId);
      }
    );

  } catch (error) {
    console.error('流式聊天失败:', error);
    // 回退到普通聊天
    await fallbackToNormalChat(messageText, responseMessageId);
  } finally {
          isLoading.value = false;
      scrollToBottom();
      saveCurrentSession();
    }
  };

// 回退到普通聊天的函数
const fallbackToNormalChat = async (messageText, responseMessageId) => {
  try {
    console.log('使用普通聊天模式');
    const response = await chatWithCoach([{ role: 'user', content: messageText }]);
    
    const messageIndex = messages.value.findIndex(m => m.id === responseMessageId);
    if (messageIndex !== -1) {
      messages.value[messageIndex].content = response.content || response.detail || '无响应内容';
      messages.value[messageIndex].isStreaming = false;
    }
  } catch (fallbackError) {
    console.error('普通聊天也失败:', fallbackError);
    const messageIndex = messages.value.findIndex(m => m.id === responseMessageId);
    if (messageIndex !== -1) {
      messages.value[messageIndex].content = `错误: ${fallbackError.message}`;
      messages.value[messageIndex].isStreaming = false;
    }
  }
};

const formatMessage = (content) => {
  // 简单的Markdown转HTML
  return content.replace(/\n/g, '<br>');
};

const saveSettings = () => {
  // 🔒 安全增强：使用sessionStorage保存API密钥
  // sessionStorage仅在浏览器会话期间有效，关闭浏览器后自动清除
  
  // 保存到sessionStorage（仅在当前浏览器会话有效）
  sessionStorage.setItem('ai_provider', apiProvider.value);
  sessionStorage.setItem('api_key', apiKey.value);
  
  // 明确不保存到localStorage（防止持久化存储）
  localStorage.removeItem('api_key');
  localStorage.removeItem('ai_provider');
  
  settingsDialogVisible.value = false;
  
  // 显示安全提示
  ElMessage.success({
    message: t('aiCoach.apiKeySet'),
    duration: 3000
  });
  
  ElMessage.info({
    message: t('aiCoach.apiKeySecurity'),
    duration: 5000
  });
  
  // 可选：设置较长时间后提醒用户（比如4小时）
  setTimeout(() => {
    if (apiKey.value) {
      ElMessage.warning({
        message: 'Security reminder: Regularly update your API keys',
        duration: 3000
      });
    }
  }, 4 * 60 * 60 * 1000); // 4小时
};

const clearApiKey = () => {
  // 清除sessionStorage中的API配置
  sessionStorage.removeItem('api_key');
  sessionStorage.removeItem('ai_provider');
  
  // 重置组件状态
  apiKey.value = '';
  apiProvider.value = 'google';
  
  // 显示确认提示
  ElMessage.success({
    message: 'API key cleared',
    duration: 2000
  });
  
  settingsDialogVisible.value = false;
};

const handleSuggestionClick = (suggestion) => {
  userInput.value = suggestion;
  sendMessage();
};

const formatTime = (date) => {
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

// 检查服务状态
const checkServiceStatus = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/data/service-status');
    const data = await response.json();
    
    if (data.status === 'success') {
      // 更新RAG状态
      const vectorDb = data.services.vector_db;
      if (vectorDb.status === 'connected') {
        ragStatus.value = {
          status: 'healthy',
          message: `RAG服务正常 (${vectorDb.vector_count?.toLocaleString() || 0} 个向量)`
        };
      } else if (vectorDb.status === 'error') {
        ragStatus.value = {
          status: 'error',
          message: `RAG连接异常: ${vectorDb.error}`
        };
      } else {
        ragStatus.value = {
          status: 'warning',
          message: 'RAG服务状态未知'
        };
      }
      
      // 更新LLM状态  
      const aiServices = data.services.ai_services;
      if (apiKey.value && aiServices.api_key_configured && aiServices.status === 'configured') {
        llmStatus.value = {
          status: 'healthy',
          message: `LLM服务正常 (${aiServices.default_provider})`
        };
      } else if (!apiKey.value || !aiServices.api_key_configured) {
        llmStatus.value = {
          status: 'warning',
          message: t('aiCoach.apiKeyRequired')
        };
      } else if (aiServices.status === 'error') {
        llmStatus.value = {
          status: 'error',
          message: `LLM连接异常: ${aiServices.error}`
        };
      } else {
        llmStatus.value = {
          status: 'warning',
          message: 'LLM服务状态未知'
        };
      }
    } else {
      ragStatus.value = { status: 'error', message: 'RAG连接失败' };
      llmStatus.value = { status: 'error', message: 'LLM检查失败' };
    }
  } catch (error) {
    console.error('检查服务状态失败:', error);
    
    // 网络错误时保持checking状态，避免频繁切换
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      ragStatus.value = { status: 'checking', message: 'RAG服务检查中...' };
      llmStatus.value = { status: 'checking', message: 'LLM服务检查中...' };
    } else {
      ragStatus.value = { status: 'error', message: 'RAG连接失败' };
      llmStatus.value = { status: 'error', message: 'LLM连接失败' };
    }
  }
};

// 获取RAG数据库信息
const refreshRagInfo = async () => {
  ragInfoLoading.value = true;
  try {
    // 获取向量统计
    const statsResponse = await fetch('http://localhost:8000/api/v1/data/vector-stats', {
      headers: {
        'Authorization': `Bearer ${sessionStorage.getItem('auth_token') || 'demo'}`
      }
    });
    
    if (statsResponse.ok) {
      const statsData = await statsResponse.json();
      ragInfo.value.vectorCount = statsData.data.vector_database.total_vectors || 0;
    }
    
    // 获取已导入文件列表
    const filesResponse = await fetch('http://localhost:8000/api/v1/data/imported-files');
    
    if (filesResponse.ok) {
      const filesData = await filesResponse.json();
      if (filesData.status === 'success') {
        ragInfo.value.files = filesData.data.files.map(file => ({
          source: file.source,
          count: file.count,
          lastImported: file.last_imported ? new Date(file.last_imported) : new Date()
        }));
        ragInfo.value.fileCount = filesData.data.total_files;
      }
    } else {
          // 即使API失败也要显示已知的CSV文件
    ragInfo.value.files = [{
      source: 'epi_r.csv',
      count: ragInfo.value.vectorCount || 0,
      lastImported: new Date(),
      status: 'API失败',
      estimated_records: 20000,
      imported_records: ragInfo.value.vectorCount || 0
    }];
    ragInfo.value.fileCount = 1;
    }
    
  } catch (error) {
    console.error('获取RAG信息失败:', error);
    ElMessage.warning('获取RAG信息失败，显示默认数据');
    
    // 即使出错也要显示CSV文件信息
    ragInfo.value.files = [{
      source: 'epi_r.csv',
      count: ragInfo.value.vectorCount || 0,
      lastImported: new Date(),
      status: '检查失败',
      estimated_records: 20000,
      imported_records: 0
    }];
    ragInfo.value.fileCount = 1;
  } finally {
    ragInfoLoading.value = false;
  }
};

// 生成向量数据
const generateVectors = async () => {
  if (!apiKey.value) {
    ElMessage.error(t('aiCoach.configureApiKeyFirst'));
    return;
  }
  
  if (!['google', 'openai', 'zhipu'].includes(apiProvider.value)) {
            ElMessage.error(t('aiCoach.vectorGenerationError'));
    return;
  }
  
  isGeneratingVectors.value = true;
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/data/generate-vectors-with-user-key', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Provider': apiProvider.value,
        'X-API-Key': apiKey.value
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `向量生成失败: ${response.status}`);
    }
    
    const result = await response.json();
    
    ElMessage.success(`向量生成成功！共生成 ${result.vector_count} 个向量，处理了 ${result.recipes_processed} 个食谱`);
    
    // 刷新RAG信息
    await refreshRagInfo();
    
  } catch (error) {
    console.error('向量生成失败:', error);
    ElMessage.error(`向量生成失败: ${error.message}`);
  } finally {
    isGeneratingVectors.value = false;
  }
};

// 获取文件图标
const getFileIcon = (filename) => {
  const ext = filename.split('.').pop()?.toLowerCase();
  switch (ext) {
    case 'csv': return '📊';
    case 'xlsx': case 'xls': return '📈';
    case 'pdf': return '📄';
    case 'docx': case 'doc': return '📝';
    case 'json': return '🔗';
    case 'txt': return '📋';
    case 'md': return '📖';
    default: return '📁';
  }
};

// 删除重复的formatDate函数声明，使用导入的版本
</script>

<style scoped>
/* 页面整体样式 */
.ai-coach-page {
  min-height: 100vh;
  background: var(--ai-coach-bg, #0a0a12);
  position: relative;
  overflow: hidden;
  color: var(--ai-coach-text, #ffffff);
  font-family: 'Geist', system-ui, sans-serif;
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 亮色模式样式 */
html:not(.dark) .ai-coach-page {
  --ai-coach-bg: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 25%, #cbd5e1 50%, #94a3b8 75%, #64748b 100%);
  --ai-coach-text: #1e293b;
  --ai-coach-card-bg: rgba(255, 255, 255, 0.8);
  --ai-coach-border: rgba(0, 0, 0, 0.1);
  --ai-coach-gradient-start: rgba(15, 23, 42, 0.9);
  --ai-coach-gradient-end: rgba(15, 23, 42, 0.4);
  --ai-coach-purple-glow: rgba(99, 102, 241, 0.15);
  --ai-coach-secondary-glow: rgba(139, 69, 19, 0.1);
  --ai-coach-accent-glow: rgba(88, 28, 135, 0.2);
}

/* 暗色模式样式 */
html.dark .ai-coach-page {
  --ai-coach-bg: #0a0a12;
  --ai-coach-text: #ffffff;
  --ai-coach-card-bg: rgba(255, 255, 255, 0.02);
  --ai-coach-border: rgba(255, 255, 255, 0.05);
  --ai-coach-gradient-start: rgba(255, 255, 255, 0.9);
  --ai-coach-gradient-end: rgba(255, 255, 255, 0.4);
  --ai-coach-purple-glow: rgba(88, 28, 135, 0.2);
  --ai-coach-secondary-glow: rgba(139, 69, 19, 0.1);
  --ai-coach-accent-glow: rgba(67, 56, 202, 0.15);
}

/* 背景层 - 与Home页面一致 */
.hero-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -2;
}

.radial-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(
      ellipse 20% 80% at 50% -20%,
      var(--ai-coach-purple-glow, rgba(75, 85, 150, 0.4)),
      transparent
    ),
    linear-gradient(
      135deg,
      var(--ai-coach-accent-glow, rgba(88, 28, 135, 0.15)) 0%,
      var(--ai-coach-secondary-glow, rgba(139, 69, 19, 0.1)) 50%,
      var(--ai-coach-purple-glow, rgba(30, 58, 138, 0.15)) 100%
    );
  transition: background 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.purple-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(
      ellipse 40% 60% at 30% 20%, 
      var(--ai-coach-accent-glow, rgba(88, 28, 135, 0.2)), 
      transparent 50%
    ),
    radial-gradient(
      ellipse 50% 80% at 70% 80%, 
      var(--ai-coach-purple-glow, rgba(67, 56, 202, 0.15)), 
      transparent 50%
    ),
    radial-gradient(
      ellipse 60% 40% at 50% 50%, 
      var(--ai-coach-secondary-glow, rgba(139, 69, 19, 0.1)), 
      transparent 50%
    );
  filter: blur(3px);
  opacity: 0.9;
  transition: background 0.8s cubic-bezier(0.4, 0, 0.2, 1), 
              opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 动画浮动blob背景 */
.animated-blobs {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  pointer-events: none;
}

.blob {
  position: absolute;
  border-radius: 50%;
  mix-blend-mode: normal;
  animation: pulse 2s infinite;
  filter: blur(128px);
}

.blob-1 {
  width: 24rem;
  height: 24rem;
  background: rgba(139, 92, 246, 0.1);
  top: 10%;
  left: 10%;
  animation-delay: 0ms;
}

.blob-2 {
  width: 24rem;
  height: 24rem;
  background: rgba(99, 102, 241, 0.1);
  top: 50%;
  right: 10%;
  animation-delay: 700ms;
}

.blob-3 {
  width: 16rem;
  height: 16rem;
  background: rgba(232, 121, 249, 0.1);
  bottom: 20%;
  left: 50%;
  animation-delay: 1000ms;
  filter: blur(96px);
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.1);
  }
}

/* 鼠标追踪光晕 */
.mouse-glow {
  position: fixed;
  width: 50rem;
  height: 50rem;
  border-radius: 50%;
  background: linear-gradient(to right, 
    rgba(139, 92, 246, 0.02), 
    rgba(232, 121, 249, 0.02), 
    rgba(99, 102, 241, 0.02)
  );
  filter: blur(96px);
  pointer-events: none;
  z-index: 0;
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

/* 主容器 */
.chat-hero-container {
  position: relative;
  z-index: 10;
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3rem;
}

/* 标题区域 */
.hero-header {
  text-align: center;
  margin-bottom: 2rem;
  opacity: 0;
  animation: fadeInUp 0.6s ease forwards;
  animation-delay: 0.2s;
}

.gradient-title {
  font-size: clamp(2rem, 6vw, 3rem);
  font-weight: 500;
  letter-spacing: -0.025em;
  margin: 0 0 1rem 0;
  line-height: 1.2;
  background: linear-gradient(
    135deg,
    var(--ai-coach-gradient-start, rgba(255, 255, 255, 0.9)) 0%,
    var(--ai-coach-gradient-end, rgba(255, 255, 255, 0.4)) 100%
  );
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  transition: background 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.title-divider {
  height: 1px;
  background: linear-gradient(
    to right,
    transparent,
    var(--ai-coach-border, rgba(255, 255, 255, 0.2)),
    transparent
  );
  width: 0%;
  margin: 1rem auto;
  animation: expandWidth 0.8s ease forwards;
  animation-delay: 0.5s;
  transition: background 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.hero-subtitle {
  font-size: 0.875rem;
  color: var(--ai-coach-text-muted, rgba(255, 255, 255, 0.4));
  margin: 0;
  opacity: 0;
  animation: fadeInUp 0.6s ease forwards;
  animation-delay: 0.3s;
  transition: color 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 在亮色模式和暗色模式中添加文字变体 */
html:not(.dark) .ai-coach-page {
  --ai-coach-text-muted: rgba(30, 41, 59, 0.6);
}

html.dark .ai-coach-page {
  --ai-coach-text-muted: rgba(255, 255, 255, 0.4);
}

/* 主容器 - 聊天框始终居中，历史面板独立固定 */
.chat-hero-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3rem;
  position: relative;
}

/* 聊天输入卡片 - 固定大小，始终居中 */
.chat-input-card {
  width: 900px;
  max-width: 900px;
  background: var(--ai-coach-card-bg, rgba(255, 255, 255, 0.02));
  border: 1px solid var(--ai-coach-border, rgba(255, 255, 255, 0.05));
  border-radius: 2rem;
  backdrop-filter: blur(24px);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  padding: 1.5rem;
  opacity: 0;
  transform: scale(0.98);
  animation: scaleIn 0.2s ease forwards;
  animation-delay: 0.1s;
  transition: all 0.3s ease;
}

/* 聊天历史侧边栏 - 完全固定在页面上 */
.history-sidebar {
  position: fixed !important;
  left: 2rem !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  width: 320px !important;
  max-height: 600px !important;
  background: var(--ai-coach-card-bg, rgba(255, 255, 255, 0.02)) !important;
  border: 1px solid var(--ai-coach-border, rgba(255, 255, 255, 0.05)) !important;
  border-radius: 1rem !important;
  backdrop-filter: blur(24px) !important;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15) !important;
  overflow: hidden !important;
  z-index: 1000 !important;
  /* 强制固定定位，不受任何其他CSS影响 */
  margin: 0 !important;
  padding: 0 !important;
}

.history-header {
  padding: 1rem;
  border-bottom: 1px solid var(--ai-coach-border, rgba(255, 255, 255, 0.05));
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.history-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--ai-coach-text, rgba(255, 255, 255, 0.9));
}

.history-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* 历史记录操作按钮样式 - 复用快捷建议按钮样式 */
.history-action-btn {
  padding: 0.5rem 1rem;
  border-radius: 1.5rem;
  background: var(--ai-coach-suggestion-bg, rgba(255, 255, 255, 0.05));
  border: 1px solid var(--ai-coach-suggestion-border, rgba(255, 255, 255, 0.1));
  color: var(--ai-coach-suggestion-text, rgba(255, 255, 255, 0.8));
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: auto;
}

.history-action-btn.close-btn {
  padding: 0.5rem;
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
}

.history-action-btn:hover {
  background: var(--ai-coach-suggestion-hover-bg, rgba(255, 255, 255, 0.1));
  color: var(--ai-coach-suggestion-hover-text, rgba(255, 255, 255, 1));
  transform: translateY(-1px);
  border-color: var(--ai-coach-suggestion-hover-border, rgba(255, 255, 255, 0.2));
}

/* 亮色模式和暗色模式适配 */
html:not(.dark) .history-action-btn {
  --ai-coach-suggestion-bg: rgba(255, 255, 255, 0.8);
  --ai-coach-suggestion-border: rgba(0, 0, 0, 0.1);
  --ai-coach-suggestion-text: rgba(30, 41, 59, 0.8);
}

html.dark .history-action-btn {
  --ai-coach-suggestion-bg: rgba(255, 255, 255, 0.05);
  --ai-coach-suggestion-border: rgba(255, 255, 255, 0.1);
  --ai-coach-suggestion-text: rgba(255, 255, 255, 0.8);
}

html:not(.dark) .history-action-btn:hover {
  --ai-coach-suggestion-hover-bg: rgba(255, 255, 255, 0.95);
  --ai-coach-suggestion-hover-text: rgba(30, 41, 59, 1);
  --ai-coach-suggestion-hover-border: rgba(0, 0, 0, 0.2);
}

html.dark .history-action-btn:hover {
  --ai-coach-suggestion-hover-bg: rgba(255, 255, 255, 0.1);
  --ai-coach-suggestion-hover-text: rgba(255, 255, 255, 1);
  --ai-coach-suggestion-hover-border: rgba(255, 255, 255, 0.2);
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
  padding: 0.5rem;
}

.history-list::-webkit-scrollbar {
  width: 4px;
}

.history-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 2px;
}

.history-list::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 2px;
}

.empty-history {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--ai-coach-text-muted, rgba(255, 255, 255, 0.4));
  font-size: 0.875rem;
}

.history-item {
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.history-item:hover {
  background: var(--ai-coach-hover-bg, rgba(255, 255, 255, 0.05));
  border-color: var(--ai-coach-hover-border, rgba(255, 255, 255, 0.1));
}

.history-item.active {
  background: var(--ai-coach-active-bg, rgba(139, 92, 246, 0.15));
  border-color: var(--ai-coach-active-border, rgba(139, 92, 246, 0.3));
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ai-coach-text, rgba(255, 255, 255, 0.9));
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-meta {
  font-size: 0.75rem;
  color: var(--ai-coach-text-muted, rgba(255, 255, 255, 0.4));
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.history-item:hover .delete-btn {
  opacity: 1;
}

/* 左侧滑动动画 */
.slide-left-enter-active {
  transition: all 0.3s ease-out;
}

.slide-left-leave-active {
  transition: all 0.3s cubic-bezier(1.0, 0.5, 0.8, 1.0);
}

.slide-left-enter-from,
.slide-left-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}

/* 亮色模式样式调整 */
html:not(.dark) .history-sidebar {
  --ai-coach-card-bg: rgba(255, 255, 255, 0.95);
  --ai-coach-border: rgba(0, 0, 0, 0.1);
  --ai-coach-text: rgba(0, 0, 0, 0.9);
  --ai-coach-text-muted: rgba(0, 0, 0, 0.6);
  --ai-coach-hover-bg: rgba(0, 0, 0, 0.05);
  --ai-coach-hover-border: rgba(0, 0, 0, 0.1);
  --ai-coach-active-bg: rgba(59, 130, 246, 0.15);
  --ai-coach-active-border: rgba(59, 130, 246, 0.3);
}

html.dark .history-sidebar {
  --ai-coach-card-bg: rgba(255, 255, 255, 0.02);
  --ai-coach-border: rgba(255, 255, 255, 0.05);
  --ai-coach-text: rgba(255, 255, 255, 0.9);
  --ai-coach-text-muted: rgba(255, 255, 255, 0.4);
  --ai-coach-hover-bg: rgba(255, 255, 255, 0.05);
  --ai-coach-hover-border: rgba(255, 255, 255, 0.1);
  --ai-coach-active-bg: rgba(139, 92, 246, 0.15);
  --ai-coach-active-border: rgba(139, 92, 246, 0.3);
}

.chat-input-card:hover {
  transform: scale(1.01);
  border-color: var(--ai-coach-hover-border, rgba(255, 255, 255, 0.1));
}

/* 添加亮色模式的悬停边框 */
html:not(.dark) .ai-coach-page {
  --ai-coach-hover-border: rgba(0, 0, 0, 0.2);
}

html.dark .ai-coach-page {
  --ai-coach-hover-border: rgba(255, 255, 255, 0.1);
}

/* 聊天消息区域 */
.chat-messages {
  max-height: 700px;
  overflow-y: auto;
  margin-bottom: 1rem;
  padding-right: 0.5rem;
}

.chat-messages::-webkit-scrollbar {
  width: 4px;
}

.chat-messages::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 2px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 2px;
}

/* 消息样式 */
.message-row {
  display: flex;
  margin-bottom: 1rem;
  align-items: flex-end;
  gap: 0.75rem;
}

.message-row.user {
  justify-content: flex-end;
}

.avatar-wrapper {
  position: relative;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.875rem;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.8), rgba(232, 121, 249, 0.8));
  z-index: 2;
  position: relative;
}

.avatar.user {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.8), rgba(139, 92, 246, 0.8));
}

.avatar-glow {
  position: absolute;
  top: -4px;
  left: -4px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: inherit;
  z-index: 1;
  opacity: 0.3;
  animation: glow 2s ease-in-out infinite alternate;
}

.message-bubble {
  max-width: 70%;
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.message-bubble.user {
  background: var(--ai-coach-user-bubble, rgba(139, 92, 246, 0.15));
  border-bottom-right-radius: 0.25rem;
}

/* 添加用户消息气泡样式 */
html:not(.dark) .message-bubble.user {
  --ai-coach-user-bubble: rgba(59, 130, 246, 0.15);
}

html.dark .message-bubble.user {
  --ai-coach-user-bubble: rgba(139, 92, 246, 0.15);
}

.message-bubble.assistant {
  background: var(--ai-coach-assistant-bubble, rgba(255, 255, 255, 0.05));
  border-bottom-left-radius: 0.25rem;
}

/* 添加助手消息气泡样式 */
html:not(.dark) .message-bubble.assistant {
  --ai-coach-assistant-bubble: rgba(0, 0, 0, 0.05);
}

html.dark .message-bubble.assistant {
  --ai-coach-assistant-bubble: rgba(255, 255, 255, 0.05);
}

.message-content {
  line-height: 1.5;
  font-size: 0.875rem;
  color: var(--ai-coach-message-text, rgba(255, 255, 255, 0.9));
  transition: color 0.3s ease;
}

/* 添加消息文字颜色变体 */
html:not(.dark) .message-content {
  --ai-coach-message-text: rgba(30, 41, 59, 0.9);
}

html.dark .message-content {
  --ai-coach-message-text: rgba(255, 255, 255, 0.9);
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.5;
  margin-top: 0.25rem;
}

/* 流式响应指示器 */
.streaming-indicator {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 0.75rem;
  color: rgba(139, 92, 246, 0.8);
}

.streaming-cursor {
  animation: blink 1s infinite;
  font-weight: bold;
}

.streaming-text {
  opacity: 0.7;
}

.message-bubble.streaming {
  border-color: rgba(139, 92, 246, 0.3);
  box-shadow: 0 0 10px rgba(139, 92, 246, 0.2);
}

.model-info {
  font-size: 0.65rem;
  opacity: 0.6;
  font-style: italic;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* 输入区域 */
.input-section {
  position: relative;
}

.chat-textarea {
  width: 100%;
  min-height: 60px;
  max-height: 200px;
  padding: 1rem;
  background: transparent;
  border: none;
  border-radius: 1rem;
  color: var(--ai-coach-input-text, rgba(255, 255, 255, 0.9));
  font-size: 1rem;
  font-family: inherit;
  resize: none;
  outline: none;
  transition: all 0.2s ease;
}

/* 添加输入框文字颜色 */
html:not(.dark) .chat-textarea {
  --ai-coach-input-text: rgba(30, 41, 59, 0.9);
}

html.dark .chat-textarea {
  --ai-coach-input-text: rgba(255, 255, 255, 0.9);
}

.chat-textarea::placeholder {
  color: var(--ai-coach-placeholder, rgba(255, 255, 255, 0.3));
}

/* 添加占位符颜色 */
html:not(.dark) .chat-textarea::placeholder {
  --ai-coach-placeholder: rgba(30, 41, 59, 0.5);
}

html.dark .chat-textarea::placeholder {
  --ai-coach-placeholder: rgba(255, 255, 255, 0.3);
}

.chat-textarea:focus {
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.3);
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.75rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: var(--ai-coach-action-bg, rgba(255, 255, 255, 0.05));
  border: 1px solid var(--ai-coach-action-border, rgba(255, 255, 255, 0.1));
  color: var(--ai-coach-action-text, rgba(255, 255, 255, 0.6));
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

/* 添加操作按钮样式变体 */
html:not(.dark) .action-btn {
  --ai-coach-action-bg: rgba(255, 255, 255, 0.8);
  --ai-coach-action-border: rgba(0, 0, 0, 0.1);
  --ai-coach-action-text: rgba(30, 41, 59, 0.7);
}

html.dark .action-btn {
  --ai-coach-action-bg: rgba(255, 255, 255, 0.05);
  --ai-coach-action-border: rgba(255, 255, 255, 0.1);
  --ai-coach-action-text: rgba(255, 255, 255, 0.6);
}

.action-btn:hover {
  background: var(--ai-coach-action-hover-bg, rgba(255, 255, 255, 0.1));
  color: var(--ai-coach-action-hover-text, rgba(255, 255, 255, 0.9));
  transform: scale(1.05);
}

/* 添加操作按钮悬停样式 */
html:not(.dark) .action-btn:hover {
  --ai-coach-action-hover-bg: rgba(255, 255, 255, 0.95);
  --ai-coach-action-hover-text: rgba(30, 41, 59, 0.9);
}

html.dark .action-btn:hover {
  --ai-coach-action-hover-bg: rgba(255, 255, 255, 0.1);
  --ai-coach-action-hover-text: rgba(255, 255, 255, 0.9);
}

.send-button {
  padding: 0.5rem 1.5rem;
  border-radius: 2rem;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.send-button:disabled {
  background: var(--ai-coach-disabled-bg, rgba(255, 255, 255, 0.05));
  color: var(--ai-coach-disabled-text, rgba(255, 255, 255, 0.4));
  cursor: not-allowed;
}

/* 添加禁用按钮样式 */
html:not(.dark) .send-button:disabled {
  --ai-coach-disabled-bg: rgba(0, 0, 0, 0.05);
  --ai-coach-disabled-text: rgba(30, 41, 59, 0.4);
}

html.dark .send-button:disabled {
  --ai-coach-disabled-bg: rgba(255, 255, 255, 0.05);
  --ai-coach-disabled-text: rgba(255, 255, 255, 0.4);
}

.send-button.enabled {
  background: #ffffff;
  color: #0a0a12;
  box-shadow: 0 4px 16px rgba(255, 255, 255, 0.1);
}

.send-button.enabled:hover {
  transform: scale(1.02);
  box-shadow: 0 6px 20px rgba(255, 255, 255, 0.15);
}

/* 服务状态区域 */
.service-status-section {
  margin-top: 2rem;
  opacity: 0;
  animation: fadeInUp 0.6s ease forwards;
  animation-delay: 0.4s;
}

.status-indicators {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 1rem;
  border: 1px solid;
  font-size: 0.75rem;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
  backdrop-filter: blur(12px);
}

.status-indicator:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.status-indicator.status-healthy {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
  color: #22c55e;
}

.status-indicator.status-warning {
  background: rgba(251, 191, 36, 0.1);
  border-color: rgba(251, 191, 36, 0.3);
  color: #fbbf24;
}

.status-indicator.status-error {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.status-indicator.status-unknown {
  background: rgba(156, 163, 175, 0.1);
  border-color: rgba(156, 163, 175, 0.3);
  color: #9ca3af;
}

.status-icon {
  font-size: 1rem;
}

.status-text {
  font-size: 0.75rem;
  font-weight: 600;
}

/* 快捷建议 */
.quick-suggestions {
  text-align: center;
  margin-top: 2rem;
  opacity: 0;
  animation: fadeInUp 0.6s ease forwards;
  animation-delay: 0.5s;
}

.suggestion-label {
  font-size: 1rem;
  color: var(--ai-coach-label-text, rgba(255, 255, 255, 0.7));
  margin-bottom: 1rem;
  font-weight: 500;
  transition: color 0.3s ease;
}

/* 添加建议标签颜色 */
html:not(.dark) .suggestion-label {
  --ai-coach-label-text: rgba(30, 41, 59, 0.8);
}

html.dark .suggestion-label {
  --ai-coach-label-text: rgba(255, 255, 255, 0.7);
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
}

.suggestion-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 2rem;
  background: var(--ai-coach-suggestion-bg, rgba(255, 255, 255, 0.05));
  border: 1px solid var(--ai-coach-suggestion-border, rgba(255, 255, 255, 0.1));
  color: var(--ai-coach-suggestion-text, rgba(255, 255, 255, 0.8));
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(12px);
}

/* 添加建议按钮样式变体 */
html:not(.dark) .suggestion-btn {
  --ai-coach-suggestion-bg: rgba(255, 255, 255, 0.8);
  --ai-coach-suggestion-border: rgba(0, 0, 0, 0.1);
  --ai-coach-suggestion-text: rgba(30, 41, 59, 0.8);
}

html.dark .suggestion-btn {
  --ai-coach-suggestion-bg: rgba(255, 255, 255, 0.05);
  --ai-coach-suggestion-border: rgba(255, 255, 255, 0.1);
  --ai-coach-suggestion-text: rgba(255, 255, 255, 0.8);
}

.suggestion-btn:hover {
  background: var(--ai-coach-suggestion-hover-bg, rgba(255, 255, 255, 0.1));
  color: var(--ai-coach-suggestion-hover-text, rgba(255, 255, 255, 1));
  transform: translateY(-2px);
  border-color: var(--ai-coach-suggestion-hover-border, rgba(255, 255, 255, 0.2));
}

/* 添加建议按钮悬停样式 */
html:not(.dark) .suggestion-btn:hover {
  --ai-coach-suggestion-hover-bg: rgba(255, 255, 255, 0.95);
  --ai-coach-suggestion-hover-text: rgba(30, 41, 59, 1);
  --ai-coach-suggestion-hover-border: rgba(0, 0, 0, 0.2);
}

html.dark .suggestion-btn:hover {
  --ai-coach-suggestion-hover-bg: rgba(255, 255, 255, 0.1);
  --ai-coach-suggestion-hover-text: rgba(255, 255, 255, 1);
  --ai-coach-suggestion-hover-border: rgba(255, 255, 255, 0.2);
}

/* 输入动画 */
.message-enter-active {
  transition: all 0.5s ease;
}

.message-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

/* 正在输入指示器 */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 5px;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: rgba(139, 92, 246, 0.8);
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.ai-thinking {
  animation: aiThinking 1.5s ease-in-out infinite;
}

@keyframes aiThinking {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 动画定义 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.98);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes expandWidth {
  from {
    width: 0%;
  }
  to {
    width: 100%;
  }
}

@keyframes glow {
  from { 
    transform: scale(1); 
    opacity: 0.3; 
  }
  to { 
    transform: scale(1.1); 
    opacity: 0.1; 
  }
}

/* 设置内容样式 */
.settings-content {
  padding: 10px 0;
}

.settings-content a {
  color: #a855f7;
  text-decoration: none;
  transition: color 0.3s ease;
}

.settings-content a:hover {
  color: #8b5cf6;
  text-decoration: underline;
}

/* RAG信息区域样式 */
.rag-info-section {
  margin-top: 16px;
}

.file-list-section {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
}

.file-item:hover {
  border-color: rgba(139, 92, 246, 0.3);
  background: rgba(139, 92, 246, 0.05);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.file-icon {
  font-size: 16px;
}

.file-details {
  flex: 1;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--ai-coach-file-name, rgba(255, 255, 255, 0.9));
  margin-bottom: 2px;
}

.file-stats {
  font-size: 12px;
  color: var(--ai-coach-file-stats, rgba(255, 255, 255, 0.5));
}

.empty-files {
  text-align: center;
  padding: 20px;
  color: var(--ai-coach-empty-files, rgba(255, 255, 255, 0.5));
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .chat-input-card {
    width: 100%;
    max-width: 90vw;
  }
  
  .history-sidebar {
    position: fixed !important;
    left: 1rem !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    width: 280px !important;
    max-height: 500px !important;
  }
}

@media (max-width: 768px) {
  .chat-hero-container {
    padding: 2rem 1rem;
    gap: 2rem;
  }
  
  .chat-input-card {
    width: 100%;
    max-width: 95vw;
    padding: 1rem;
  }
  
  .input-actions {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }
  
  .send-button {
    justify-content: center;
  }
  
  .suggestions {
    flex-direction: column;
  }
  
  .status-indicators {
    flex-direction: column;
    align-items: center;
  }
  
  .file-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  /* 历史侧边栏在小屏幕上的固定定位 */
  .history-sidebar {
    position: fixed !important;
    left: 0.5rem !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    width: 260px !important;
    max-height: 400px !important;
  }
  
  .history-actions {
    gap: 0.25rem;
  }
  
  .history-action-btn {
    font-size: 0.7rem;
    padding: 0.4rem 0.8rem;
  }
  
  .history-action-btn.close-btn {
    width: 1.8rem;
    height: 1.8rem;
    padding: 0.4rem;
  }
}

/* 减少动画支持 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* API设置对话框样式 */
.api-settings-dialog {
  --el-dialog-bg: var(--ai-coach-card-bg, rgba(255, 255, 255, 0.95));
  --el-dialog-border-radius: 1rem;
  border-radius: 1rem;
}

.api-settings-dialog .el-dialog__header {
  background: var(--ai-coach-card-bg, rgba(255, 255, 255, 0.95));
  border-radius: 1rem 1rem 0 0;
  border-bottom: 1px solid var(--ai-coach-border, rgba(255, 255, 255, 0.1));
  padding: 1.5rem;
}

.api-settings-dialog .el-dialog__body {
  background: var(--ai-coach-card-bg, rgba(255, 255, 255, 0.95));
  padding: 1.5rem;
}

.api-settings-dialog .el-dialog__footer {
  background: var(--ai-coach-card-bg, rgba(255, 255, 255, 0.95));
  border-radius: 0 0 1rem 1rem;
  border-top: 1px solid var(--ai-coach-border, rgba(255, 255, 255, 0.1));
  padding: 1.5rem;
}

/* 配置指南卡片样式 */
.config-guide-card {
  background: var(--ai-coach-input-bg, rgba(255, 255, 255, 0.05));
  border: 1px solid var(--ai-coach-border, rgba(255, 255, 255, 0.1));
  border-radius: 0.75rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
  backdrop-filter: blur(12px);
}

.config-guide-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--ai-coach-text, rgba(255, 255, 255, 0.9));
  font-size: 1rem;
  font-weight: 600;
}

.config-guide-card p {
  margin: 0;
  color: var(--ai-coach-text-secondary, rgba(255, 255, 255, 0.7));
  font-size: 0.875rem;
  line-height: 1.5;
}

/* 设置页面底部按钮样式 */
.settings-footer {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  align-items: center;
}

.settings-btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--ai-coach-border, rgba(255, 255, 255, 0.1));
  background: var(--ai-coach-input-bg, rgba(255, 255, 255, 0.05));
  color: var(--ai-coach-text, rgba(255, 255, 255, 0.9));
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(12px);
  outline: none;
}

.settings-btn:hover {
  background: var(--ai-coach-input-bg-hover, rgba(255, 255, 255, 0.1));
  border-color: var(--ai-coach-border-hover, rgba(255, 255, 255, 0.2));
  transform: translateY(-1px);
}

.settings-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.settings-btn.cancel-btn {
  background: var(--ai-coach-input-bg, rgba(255, 255, 255, 0.05));
}

.settings-btn.clear-btn {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: rgba(239, 68, 68, 0.9);
}

.settings-btn.clear-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.5);
}

.settings-btn.save-btn {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
  color: rgba(59, 130, 246, 0.9);
}

.settings-btn.save-btn:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.5);
}

.settings-btn.generate-btn {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
  color: rgba(34, 197, 94, 0.9);
}

.settings-btn.generate-btn:hover {
  background: rgba(34, 197, 94, 0.2);
  border-color: rgba(34, 197, 94, 0.5);
}

.settings-btn.refresh-btn {
  background: rgba(168, 85, 247, 0.1);
  border-color: rgba(168, 85, 247, 0.3);
  color: rgba(168, 85, 247, 0.9);
}

.settings-btn.refresh-btn:hover {
  background: rgba(168, 85, 247, 0.2);
  border-color: rgba(168, 85, 247, 0.5);
}

/* 对话框关闭按钮样式 */
.api-settings-dialog .el-dialog__headerbtn {
  background: var(--ai-coach-input-bg, rgba(255, 255, 255, 0.05)) !important;
  border: 1px solid var(--ai-coach-border, rgba(255, 255, 255, 0.1)) !important;
  border-radius: 0.5rem !important;
  width: 32px !important;
  height: 32px !important;
  top: 1.5rem !important;
  right: 1.5rem !important;
  backdrop-filter: blur(12px) !important;
  transition: all 0.3s ease !important;
}

.api-settings-dialog .el-dialog__headerbtn:hover {
  background: var(--ai-coach-input-bg-hover, rgba(255, 255, 255, 0.1)) !important;
  border-color: var(--ai-coach-border-hover, rgba(255, 255, 255, 0.2)) !important;
  transform: translateY(-1px) !important;
}

.api-settings-dialog .el-dialog__headerbtn .el-dialog__close {
  color: var(--ai-coach-text, rgba(255, 255, 255, 0.9)) !important;
  font-size: 16px !important;
}



/* API设置弹窗新增样式 */
.option-tag {
  float: right;
  font-size: 13px;
  color: var(--ai-coach-option-tag, #8492a6);
}

.api-hint-text {
  margin-top: 8px;
  font-size: 12px;
  color: var(--ai-coach-hint-text, #909399);
}

.support-text {
  color: var(--ai-coach-support-text, #67c23a);
}

.warning-text {
  color: var(--ai-coach-warning-text, #e6a23c);
}

.info-text {
  color: var(--ai-coach-info-text, #f56c6c);
}

.rag-section-title {
  color: var(--ai-coach-section-title, #606266);
  font-weight: 600;
}

.provider-switch-hint {
  color: var(--ai-coach-warning-text, #e6a23c);
  font-size: 13px;
}

.file-list-title {
  font-weight: 600;
  color: var(--ai-coach-section-title, #606266);
}

/* 亮色模式适配 */
html:not(.dark) .api-settings-dialog {
  --ai-coach-card-bg: rgba(255, 255, 255, 0.95);
  --ai-coach-border: rgba(0, 0, 0, 0.1);
  --ai-coach-input-bg: rgba(0, 0, 0, 0.02);
  --ai-coach-input-bg-hover: rgba(0, 0, 0, 0.05);
  --ai-coach-border-hover: rgba(0, 0, 0, 0.15);
  --ai-coach-text: rgba(30, 41, 59, 0.9);
  --ai-coach-text-secondary: rgba(30, 41, 59, 0.7);
  --ai-coach-option-tag: rgba(30, 41, 59, 0.6);
  --ai-coach-hint-text: rgba(30, 41, 59, 0.6);
  --ai-coach-support-text: #059669;
  --ai-coach-warning-text: #d97706;
  --ai-coach-info-text: #dc2626;
  --ai-coach-section-title: rgba(30, 41, 59, 0.8);
  --ai-coach-file-name: rgba(30, 41, 59, 0.9);
  --ai-coach-file-stats: rgba(30, 41, 59, 0.6);
  --ai-coach-empty-files: rgba(30, 41, 59, 0.5);
}

/* Element Plus 组件样式覆盖 - 亮色模式 */
html:not(.dark) .api-settings-dialog .el-dialog__title {
  color: rgba(30, 41, 59, 0.9) !important;
}

html:not(.dark) .api-settings-dialog .el-form-item__label {
  color: rgba(30, 41, 59, 0.8) !important;
}

html:not(.dark) .config-guide-card {
  background: rgba(0, 0, 0, 0.02);
  border-color: rgba(0, 0, 0, 0.1);
}

html:not(.dark) .settings-btn {
  background: rgba(0, 0, 0, 0.02);
  border-color: rgba(0, 0, 0, 0.1);
  color: rgba(30, 41, 59, 0.9);
}

html:not(.dark) .settings-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.15);
}

html:not(.dark) .settings-btn.generate-btn {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
  color: rgba(34, 197, 94, 0.9);
}

html:not(.dark) .settings-btn.refresh-btn {
  background: rgba(168, 85, 247, 0.1);
  border-color: rgba(168, 85, 247, 0.3);
  color: rgba(168, 85, 247, 0.9);
}

html:not(.dark) .api-settings-dialog .el-dialog__headerbtn {
  background: rgba(0, 0, 0, 0.02) !important;
  border-color: rgba(0, 0, 0, 0.1) !important;
}

html:not(.dark) .api-settings-dialog .el-dialog__headerbtn:hover {
  background: rgba(0, 0, 0, 0.05) !important;
  border-color: rgba(0, 0, 0, 0.15) !important;
}

html:not(.dark) .api-settings-dialog .el-dialog__headerbtn .el-dialog__close {
  color: rgba(30, 41, 59, 0.9) !important;
}

/* 深色模式适配 */
html.dark .api-settings-dialog {
  --ai-coach-card-bg: rgba(255, 255, 255, 0.02);
  --ai-coach-border: rgba(255, 255, 255, 0.1);
  --ai-coach-input-bg: rgba(255, 255, 255, 0.05);
  --ai-coach-input-bg-hover: rgba(255, 255, 255, 0.1);
  --ai-coach-border-hover: rgba(255, 255, 255, 0.2);
  --ai-coach-text: rgba(255, 255, 255, 0.9);
  --ai-coach-text-secondary: rgba(255, 255, 255, 0.7);
  --ai-coach-option-tag: rgba(255, 255, 255, 0.6);
  --ai-coach-hint-text: rgba(255, 255, 255, 0.6);
  --ai-coach-support-text: #67c23a;
  --ai-coach-warning-text: #e6a23c;
  --ai-coach-info-text: #f56c6c;
  --ai-coach-section-title: rgba(255, 255, 255, 0.8);
  --ai-coach-file-name: rgba(255, 255, 255, 0.9);
  --ai-coach-file-stats: rgba(255, 255, 255, 0.5);
  --ai-coach-empty-files: rgba(255, 255, 255, 0.5);
}
</style>

<style>
/* 全局样式：el-dialog 会 Teleport 到 body，需使用全局选择器覆盖 */

/* 亮色模式变量（作用于对话框本体，供子元素继承） */
html:not(.dark) .api-settings-dialog {
  --ai-coach-card-bg: rgba(255, 255, 255, 0.95);
  --ai-coach-border: rgba(0, 0, 0, 0.1);
  --ai-coach-input-bg: rgba(0, 0, 0, 0.02);
  --ai-coach-input-bg-hover: rgba(0, 0, 0, 0.05);
  --ai-coach-border-hover: rgba(0, 0, 0, 0.15);
  --ai-coach-text: rgba(30, 41, 59, 0.9);
  --ai-coach-text-secondary: rgba(30, 41, 59, 0.7);
  --ai-coach-option-tag: rgba(30, 41, 59, 0.6);
  --ai-coach-hint-text: rgba(30, 41, 59, 0.6);
  --ai-coach-support-text: #059669;
  --ai-coach-warning-text: #d97706;
  --ai-coach-info-text: #dc2626;
  --ai-coach-section-title: rgba(30, 41, 59, 0.8);
  --ai-coach-file-name: rgba(30, 41, 59, 0.9);
  --ai-coach-file-stats: rgba(30, 41, 59, 0.6);
  --ai-coach-empty-files: rgba(30, 41, 59, 0.5);
}

/* 深色模式变量（与 scoped 中保持一致，确保全局也能继承） */
html.dark .api-settings-dialog {
  --ai-coach-card-bg: rgba(255, 255, 255, 0.02);
  --ai-coach-border: rgba(255, 255, 255, 0.1);
  --ai-coach-input-bg: rgba(255, 255, 255, 0.05);
  --ai-coach-input-bg-hover: rgba(255, 255, 255, 0.1);
  --ai-coach-border-hover: rgba(255, 255, 255, 0.2);
  --ai-coach-text: rgba(255, 255, 255, 0.9);
  --ai-coach-text-secondary: rgba(255, 255, 255, 0.7);
  --ai-coach-option-tag: rgba(255, 255, 255, 0.6);
  --ai-coach-hint-text: rgba(255, 255, 255, 0.6);
  --ai-coach-support-text: #67c23a;
  --ai-coach-warning-text: #e6a23c;
  --ai-coach-info-text: #f56c6c;
  --ai-coach-section-title: rgba(255, 255, 255, 0.8);
  --ai-coach-file-name: rgba(255, 255, 255, 0.9);
  --ai-coach-file-stats: rgba(255, 255, 255, 0.5);
  --ai-coach-empty-files: rgba(255, 255, 255, 0.5);
}

/* 配置说明卡片与文本颜色（对话框内的内容） */
.api-settings-dialog .config-guide-card {
  background: var(--ai-coach-input-bg, rgba(255, 255, 255, 0.05));
  border: 1px solid var(--ai-coach-border, rgba(255, 255, 255, 0.1));
}
.api-settings-dialog .config-guide-card h4 {
  color: var(--ai-coach-text, rgba(255, 255, 255, 0.9));
}
.api-settings-dialog .config-guide-card p {
  color: var(--ai-coach-text-secondary, rgba(255, 255, 255, 0.7));
}

/* 文件列表标题与信息颜色 */
.api-settings-dialog .file-list-title { color: var(--ai-coach-section-title, #606266); }
.api-settings-dialog .file-name { color: var(--ai-coach-file-name, rgba(255, 255, 255, 0.9)); }
.api-settings-dialog .file-stats { color: var(--ai-coach-file-stats, rgba(255, 255, 255, 0.5)); }

/* 提示文本与右侧标记 */
.api-settings-dialog .api-hint-text { color: var(--ai-coach-hint-text, #909399); }
.api-settings-dialog .option-tag { color: var(--ai-coach-option-tag, #8492a6); }

/* 亮色模式下提升“生成向量数据”按钮的可读性 */
html:not(.dark) .api-settings-dialog .settings-btn.generate-btn {
  background: rgba(34, 197, 94, 0.18) !important;
  border-color: rgba(34, 197, 94, 0.45) !important;
  color: #047857 !important; /* 深绿文字，提高对比度 */
}
html:not(.dark) .api-settings-dialog .settings-btn.generate-btn:hover {
  background: rgba(34, 197, 94, 0.28) !important;
  border-color: rgba(34, 197, 94, 0.55) !important;
}
</style>
