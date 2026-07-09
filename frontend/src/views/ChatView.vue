<template>
  <div class="chat-page">
    <header class="chat-header">
      <div class="header-left">
        <h2 class="page-title">
          <el-icon color="var(--accent-cyan)"><ChatDotRound /></el-icon>
          AI 对话
        </h2>
        <span v-if="chat.currentSessionId" class="session-badge">
          <span class="badge-dot"></span>
          {{ currentSession?.title }}
        </span>
      </div>
      <div class="header-right">
        <el-button class="btn-ghost-sm" @click="handleNewSession">
          <el-icon><Plus /></el-icon> 新建会话
        </el-button>
        <el-button class="btn-ghost-sm" @click="showShortcuts = true">
          <el-icon><Operation /></el-icon> 快捷指令
        </el-button>
      </div>
    </header>

    <div class="chat-body">
      <aside class="session-list">
        <div class="session-list-header">
          <span>会话列表</span>
          <el-button text size="small" @click="handleNewSession"><el-icon><Plus /></el-icon></el-button>
        </div>
        <div class="sessions">
          <div v-if="chat.sessions.length === 0" class="empty-sessions">
            <el-icon :size="28" color="var(--text-muted)"><ChatLineRound /></el-icon>
            <p>暂无会话</p>
          </div>
          <div
            v-for="s in chat.sessions" :key="s.id"
            class="session-item"
            :class="{ active: s.id === chat.currentSessionId }"
            @click="selectSession(s)"
          >
            <el-icon class="session-icon"><ChatLineRound /></el-icon>
            <div class="session-info">
              <span class="session-title">{{ s.title }}</span>
              <span class="session-date">{{ formatDate(s.updated_at) }}</span>
            </div>
            <el-button text size="small" class="delete-btn" @click.stop="removeSession(s.id)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </aside>

      <div class="chat-area">
        <div v-if="!chat.currentSessionId && chat.messages.length === 0" class="welcome-screen">
          <div class="welcome-icon glow-border">
            <svg width="88" height="88" viewBox="0 0 88 88" fill="none">
              <rect width="88" height="88" rx="24" fill="url(#wg2)"/>
              <path d="M26 44l12 12 24-24" stroke="#fff" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
              <defs>
                <linearGradient id="wg2" x1="0" y1="0" x2="88" y2="88">
                  <stop stop-color="#4d8ef8"/><stop offset="1" stop-color="#22d3ee"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h2>欢迎使用 AI 代码工作台</h2>
          <p>基于预置知识库 + RAG 向量检索，助您高效解决编程问题</p>
          <div class="quick-prompts">
            <button v-for="p in quickPrompts" :key="p.text" class="prompt-btn" @click="sendQuickPrompt(p.text)">
              <el-icon :color="p.color"><component :is="p.icon" /></el-icon>
              {{ p.text }}
            </button>
          </div>
        </div>

        <div class="messages" ref="messagesEl" v-else>
          <div v-for="(msg, idx) in chat.messages" :key="msg.id || idx" class="message-row" :class="msg.role">
            <div class="avatar" :class="msg.role">
              <el-avatar :size="34" :style="msg.role === 'user' ? 'background: linear-gradient(135deg,#4d8ef8,#22d3ee)' : 'background: var(--bg-tertiary); border: 1px solid var(--border-color)'">
                {{ msg.role === 'user' ? 'U' : 'AI' }}
              </el-avatar>
            </div>
            <div class="message-content">
              <div :class="['bubble', `bubble-${msg.role}`]">
                <span v-if="msg.role === 'assistant'" class="ai-label">AI 助手</span>
                {{ msg.content }}
              </div>
              <div class="msg-time">{{ formatDate(msg.created_at) }}</div>
            </div>
          </div>

          <div v-if="chat.isStreaming && chat.streamingContent" class="message-row assistant">
            <div class="avatar assistant">
              <el-avatar :size="34" style="background: var(--bg-tertiary); border: 1px solid var(--border-color)">AI</el-avatar>
            </div>
            <div class="message-content">
              <div class="bubble bubble-assistant">
                <span class="ai-label">AI 助手</span>
                {{ chat.streamingContent }}<span class="cursor">▋</span>
              </div>
            </div>
          </div>
        </div>

        <div class="chat-input-area">
          <div class="input-wrapper" :class="{ streaming: chat.isStreaming }">
            <textarea
              v-model="inputText"
              class="chat-input"
              :placeholder="chat.isStreaming ? 'AI 正在思考中，请稍候...' : '输入消息，Shift+Enter 换行，Enter 发送'"
              :disabled="chat.isStreaming"
              @keydown.enter.exact.prevent="handleSend"
              rows="1"
            ></textarea>
            <button class="send-btn" :class="{ active: inputText.trim() && !chat.isStreaming }" @click="handleSend">
              <el-icon v-if="!chat.isStreaming"><Promotion /></el-icon>
              <el-icon v-else class="spinning"><Loading /></el-icon>
            </button>
          </div>
          <div class="input-footer">
            <span class="input-hint">💡 AI 助手基于预置知识库 RAG 检索，支持离线使用</span>
            <span class="token-hint" v-if="chat.messages.length > 0">{{ chat.messages.length }} 条消息</span>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="showShortcuts" title="快捷指令" width="560px" class="shortcuts-dialog">
      <div class="shortcuts-grid">
        <div v-for="s in shortcuts" :key="s.label" class="shortcut-item glow-border" @click="sendQuickPrompt(s.prompt)">
          <el-icon :color="s.color" :size="20"><component :is="s.icon" /></el-icon>
          <span class="shortcut-label">{{ s.label }}</span>
          <span class="shortcut-prompt">{{ s.prompt }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { useChatStore } from '../stores/chat'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { ChatSession } from '../types'

const chat = useChatStore()
const inputText = ref('')
const messagesEl = ref<HTMLElement>()
const showShortcuts = ref(false)

const currentSession = computed(() => chat.sessions.find(s => s.id === chat.currentSessionId))

const quickPrompts = [
  { icon: 'Sort', color: '#fb923c', text: 'Git rebase 和 merge 区别' },
  { icon: 'Box', color: '#4d8ef8', text: 'Docker Compose 启动多服务' },
  { icon: 'Cpu', color: '#a78bfa', text: 'Python async/await 用法' },
  { icon: 'Connection', color: '#10b981', text: 'Redis 分布式锁原理' },
]

const shortcuts = [
  { label: 'Git', prompt: 'Git 常用命令有哪些？', icon: 'Sort', color: '#fb923c' },
  { label: 'Docker', prompt: 'Dockerfile 最佳实践', icon: 'Box', color: '#4d8ef8' },
  { label: 'SQL', prompt: 'SQL 索引优化技巧', icon: 'DataAnalysis', color: '#10b981' },
  { label: 'Python', prompt: 'Python 装饰器详解', icon: 'Cpu', color: '#a78bfa' },
  { label: '系统设计', prompt: '高并发系统架构设计要点', icon: 'Connection', color: '#22d3ee' },
  { label: '前端', prompt: 'Vue3 组合式 API 怎么用', icon: 'Monitor', color: '#fb923c' },
  { label: 'Redis', prompt: 'Redis 缓存策略有哪些', icon: 'Connection', color: '#f87171' },
  { label: '网络', prompt: 'TCP 三次握手四次挥手', icon: 'Connection', color: '#4d8ef8' },
  { label: 'FastAPI', prompt: 'FastAPI 中间件怎么写', icon: 'Cpu', color: '#10b981' },
]

function formatDate(dt: string) {
  const d = new Date(dt)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString('zh-CN')
}

async function selectSession(s: ChatSession) { await chat.loadMessages(s.id) }
async function handleNewSession() {
  const s = await chat.createSession()
  await chat.loadMessages(s.id)
}
async function removeSession(id: number) {
  await ElMessageBox.confirm('确定删除该会话？', '提示', { type: 'warning' })
  await chat.deleteSession(id)
  ElMessage.success('已删除')
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  })
}

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || chat.isStreaming) return
  inputText.value = ''
  await chat.sendMessage(text, scrollToBottom, scrollToBottom)
}

async function sendQuickPrompt(prompt: string) {
  showShortcuts.value = false
  if (!chat.currentSessionId) await chat.createSession(prompt.slice(0, 20))
  inputText.value = prompt
  await handleSend()
}

onMounted(() => { chat.loadSessions() })
</script>

<style scoped>
.chat-page { display: flex; flex-direction: column; height: 100vh; }

.chat-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 24px; border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}
.header-left { display: flex; align-items: center; gap: 12px; }
.page-title { display: flex; align-items: center; gap: 8px; font-size: 1.05rem; font-weight: 700; color: var(--text-primary); }
.session-badge { display: flex; align-items: center; gap: 6px; font-size: .75rem; color: var(--text-muted); background: var(--bg-tertiary); padding: 3px 10px; border-radius: 20px; border: 1px solid var(--border-color); }
.badge-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent-green); }
.header-right { display: flex; gap: 8px; }
.btn-ghost-sm { display: flex; align-items: center; gap: 4px; padding: 6px 12px; background: transparent; border: 1px solid var(--border-color); border-radius: var(--radius-sm); color: var(--text-secondary); font-size: .8rem; cursor: pointer; transition: all .2s; }
.btn-ghost-sm:hover { border-color: var(--accent-blue); color: var(--accent-blue); }

.chat-body { flex: 1; display: flex; overflow: hidden; }

.session-list { width: 220px; flex-shrink: 0; border-right: 1px solid var(--border-color); display: flex; flex-direction: column; background: var(--bg-secondary); }
.session-list-header { padding: 14px 16px; font-size: .72rem; color: var(--text-muted); letter-spacing: 1px; text-transform: uppercase; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); }
.sessions { flex: 1; overflow-y: auto; padding: 8px; }
.empty-sessions { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 32px 0; }
.empty-sessions p { font-size: .78rem; color: var(--text-muted); }
.session-item { display: flex; align-items: center; gap: 8px; padding: 10px 8px; border-radius: var(--radius-sm); cursor: pointer; transition: all .2s; position: relative; }
.session-item:hover, .session-item.active { background: var(--bg-tertiary); }
.session-item.active { border-left: 2px solid var(--accent-blue); }
.session-icon { color: var(--text-muted); flex-shrink: 0; }
.session-info { flex: 1; min-width: 0; }
.session-title { display: block; font-size: .8rem; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.session-date { font-size: .65rem; color: var(--text-muted); }
.delete-btn { opacity: 0; transition: opacity .2s; }
.session-item:hover .delete-btn { opacity: 1; }

.chat-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.welcome-screen { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; padding: 40px; text-align: center; }
.welcome-icon { margin-bottom: 8px; border-radius: 24px; padding: 4px; }
.welcome-screen h2 { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); }
.welcome-screen p { color: var(--text-secondary); font-size: .85rem; max-width: 400px; }
.quick-prompts { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-top: 8px; }
.prompt-btn { display: flex; align-items: center; gap: 6px; padding: 8px 16px; background: var(--bg-tertiary); border: 1px solid var(--border-color); border-radius: 20px; color: var(--text-secondary); font-size: .8rem; cursor: pointer; transition: all .2s; }
.prompt-btn:hover { border-color: var(--accent-blue); color: var(--accent-blue); transform: translateY(-1px); }

.messages { flex: 1; overflow-y: auto; padding: 20px 24px; display: flex; flex-direction: column; gap: 20px; }
.message-row { display: flex; gap: 12px; align-items: flex-start; }
.message-row.user { flex-direction: row-reverse; }
.avatar { flex-shrink: 0; margin-top: 2px; }
.message-content { max-width: 74%; }
.bubble { padding: 14px 18px; font-size: .88rem; line-height: 1.7; white-space: pre-wrap; word-break: break-word; }
.bubble-user { background: linear-gradient(135deg, var(--accent-blue), #2563eb); color: #fff; border-radius: 18px 18px 6px 18px; box-shadow: 0 4px 16px rgba(77,142,248,.3); border: 1px solid rgba(255,255,255,.1); }
.bubble-assistant { background: linear-gradient(135deg, var(--bg-tertiary), rgba(26,34,53,.9)); border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 18px 18px 18px 6px; box-shadow: var(--shadow-sm); }
.ai-label { display: inline-block; font-size: .65rem; font-weight: 700; color: var(--accent-cyan); margin-bottom: 6px; letter-spacing: .5px; }
.msg-time { font-size: .65rem; color: var(--text-muted); margin-top: 4px; }
.cursor { animation: blink 1s step-end infinite; color: var(--accent-cyan); }
@keyframes blink { 50% { opacity: 0; } }

.chat-input-area { padding: 12px 24px 16px; border-top: 1px solid var(--border-color); }
.input-wrapper { display: flex; gap: 10px; align-items: flex-end; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 10px 14px; transition: border-color .2s, box-shadow .2s; }
.input-wrapper:focus-within { border-color: var(--accent-blue); box-shadow: 0 0 0 3px rgba(77,142,248,.1); }
.input-wrapper.streaming { border-color: var(--accent-orange); }
.chat-input { flex: 1; background: transparent; border: none; outline: none; color: var(--text-primary); font-size: .88rem; resize: none; max-height: 120px; line-height: 1.6; }
.chat-input::placeholder { color: var(--text-muted); }
.send-btn { width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; background: var(--bg-tertiary); border: 1px solid var(--border-color); border-radius: 8px; color: var(--text-muted); cursor: pointer; flex-shrink: 0; transition: all .2s; }
.send-btn.active { background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan)); border: none; color: #fff; box-shadow: 0 2px 12px rgba(77,142,248,.4); }
.send-btn.active:hover { transform: scale(1.05); }
.spinning { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.input-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; }
.input-hint { font-size: .68rem; color: var(--text-muted); }
.token-hint { font-size: .68rem; color: var(--text-muted); }

.shortcuts-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.shortcut-item { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 18px 12px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: var(--radius-md); cursor: pointer; transition: all .2s; text-align: center; }
.shortcut-item:hover { border-color: rgba(77,142,248,.5); transform: translateY(-2px); box-shadow: 0 4px 16px rgba(77,142,248,.15); }
.shortcut-label { font-size: .82rem; font-weight: 600; color: var(--text-primary); }
.shortcut-prompt { font-size: .68rem; color: var(--text-muted); line-height: 1.4; }
</style>
