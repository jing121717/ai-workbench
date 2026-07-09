import { defineStore } from 'pinia'
import { ref } from 'vue'
import { chatApi, knowledgeApi } from '../api/client'
import type { ChatSession, ChatMessage } from '../types'

export const useChatStore = defineStore('chat', () => {
  const sessions = ref<ChatSession[]>([])
  const currentSessionId = ref<number | null>(null)
  const messages = ref<ChatMessage[]>([])
  const streamingContent = ref('')
  const isStreaming = ref(false)

  async function loadSessions() {
    const { data } = await chatApi.listSessions()
    sessions.value = data
  }

  async function createSession(title?: string) {
    const { data } = await chatApi.createSession(title || '新会话')
    sessions.value.unshift(data)
    currentSessionId.value = data.id
    messages.value = []
    return data
  }

  async function loadMessages(sessionId: number) {
    currentSessionId.value = sessionId
    const { data } = await chatApi.listMessages(sessionId)
    messages.value = data
  }

  async function deleteSession(sessionId: number) {
    await chatApi.deleteSession(sessionId)
    sessions.value = sessions.value.filter(s => s.id !== sessionId)
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = sessions.value[0]?.id || null
      messages.value = []
    }
  }

  async function sendMessage(content: string, onChunk?: (text: string) => void, onDone?: () => void) {
    isStreaming.value = true
    streamingContent.value = ''
    messages.value.push({ id: Date.now(), session_id: currentSessionId.value || 0, role: 'user', content, created_at: new Date().toISOString() })

    let sessionId = currentSessionId.value || null
    let fullResponse = ''

    const token = localStorage.getItem('token') || ''
    const url = `${import.meta.env.VITE_API_BASE || 'http://localhost:8000'}/api/v1/chat/stream`
    const headers: Record<string, string> = { 'Content-Type': 'application/json' }
    if (token) headers['Authorization'] = `Bearer ${token}`

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify({ session_id: sessionId, message: content }),
      })

      const reader = response.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const parsed = JSON.parse(line.slice(6))
              if (parsed.content) {
                fullResponse += parsed.content
                streamingContent.value = fullResponse
                onChunk?.(fullResponse)
              }
            } catch {}
          } else if (line.startsWith('event: metadata')) {
            // metadata event
          } else if (line.startsWith('event: done')) {
            onDone?.()
          }
        }
      }
    } catch (err) {
      fullResponse = '抱歉，网络连接失败，请检查后端服务是否启动。'
    }

    if (fullResponse && !messages.value.some(m => m.role === 'assistant' && m.content === fullResponse)) {
      messages.value.push({
        id: Date.now() + 1,
        session_id: currentSessionId.value || 0,
        role: 'assistant',
        content: fullResponse,
        created_at: new Date().toISOString(),
      })
    }

    isStreaming.value = false
    streamingContent.value = ''
    await loadSessions()
  }

  return { sessions, currentSessionId, messages, streamingContent, isStreaming, loadSessions, createSession, loadMessages, deleteSession, sendMessage }
})
