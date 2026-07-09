import axios from 'axios'
import type { LoginForm, TokenResponse, UserInfo, ChatSession, ChatMessage, Document } from '../types'

const BASE_URL = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const api = axios.create({ baseURL: BASE_URL, timeout: 30000 })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authApi = {
  login(form: LoginForm) {
    return api.post<TokenResponse>('/api/v1/auth/login', form)
  },
  register(form: { username: string; password: string; nickname?: string }) {
    return api.post<TokenResponse>('/api/v1/auth/register', form)
  },
  me() {
    return api.get<UserInfo>('/api/v1/auth/me')
  },
}

export const chatApi = {
  listSessions() {
    return api.get<ChatSession[]>('/api/v1/chat/sessions')
  },
  createSession(title: string) {
    return api.post<ChatSession>('/api/v1/chat/sessions', { title })
  },
  deleteSession(sessionId: number) {
    return api.delete(`/api/v1/chat/sessions/${sessionId}`)
  },
  listMessages(sessionId: number) {
    return api.get<ChatMessage[]>(`/api/v1/chat/sessions/${sessionId}/messages`)
  },
  streamChat(sessionId: number | null, message: string) {
    return `${BASE_URL}/api/v1/chat/stream`
  },
}

export const knowledgeApi = {
  listDocuments(params?: { skip?: number; limit?: number }) {
    return api.get<{ total: number; results: Document[] }>('/api/v1/knowledge/documents', { params })
  },
  uploadDocument(file: File) {
    const form = new FormData()
    form.append('file', file)
    return api.post('/api/v1/knowledge/upload', form)
  },
  deleteDocument(docId: number) {
    return api.delete(`/api/v1/knowledge/documents/${docId}`)
  },
}

export const codeProjectApi = {
  listProjects() {
    return api.get('/api/v1/code-projects/')
  },
  getProject(projectId: number) {
    return api.get(`/api/v1/code-projects/${projectId}`)
  },
  getStructure(projectId: number) {
    return api.get(`/api/v1/code-projects/${projectId}/structure`)
  },
  getUnits(projectId: number, params?: { unit_type?: string; file_path?: string; page?: number; page_size?: number }) {
    return api.get(`/api/v1/code-projects/${projectId}/units`, { params })
  },
  syncProject(projectId: number) {
    return api.post(`/api/v1/code-projects/${projectId}/sync`)
  },
  gitClone(payload: { url: string; local_path?: string; branch?: string }) {
    return api.post('/api/v1/code-projects/git-clone', payload)
  },
}

export const codeAiApi = {
  analyze(payload: { code: string; language: string; analysis_type: string }) {
    return api.post('/api/v1/code-ai/analyze', payload)
  },
  convert(payload: { code: string; source_language: string; target_language: string; framework?: string }) {
    return api.post('/api/v1/code-ai/convert', payload)
  },
  unitTest(payload: { code: string; language: string; framework?: string }) {
    return api.post('/api/v1/code-ai/unit-test', payload)
  },
  apiDoc(payload: { code: string; language: string }) {
    return api.post('/api/v1/code-ai/api-doc', payload)
  },
  logAnalyze(payload: { log_content: string; error_type?: string; code?: string }) {
    return api.post('/api/v1/code-ai/log-analyze', payload)
  },
  refactor(payload: { code: string; language: string; refactor_type?: string }) {
    return api.post('/api/v1/code-ai/refactor', payload)
  },
}

export const snippetApi = {
  list(params?: Record<string, unknown>) {
    return api.get('/api/v1/snippets/', { params })
  },
  detail(snippetId: number) {
    return api.get(`/api/v1/snippets/${snippetId}`)
  },
  create(payload: Record<string, unknown>) {
    return api.post('/api/v1/snippets/', payload)
  },
  update(snippetId: number, payload: Record<string, unknown>) {
    return api.put(`/api/v1/snippets/${snippetId}`, payload)
  },
  remove(snippetId: number) {
    return api.delete(`/api/v1/snippets/${snippetId}`)
  },
  favorite(snippetId: number) {
    return api.post(`/api/v1/snippets/${snippetId}/favorite`)
  },
  categories() {
    return api.get('/api/v1/snippets/categories/list')
  },
  tags() {
    return api.get('/api/v1/snippets/tags/cloud')
  },
}

export default api
