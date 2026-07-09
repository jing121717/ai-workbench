export interface LoginForm {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user_id: number
  username: string
}

export interface UserInfo {
  id: number
  username: string
  nickname: string
  is_superuser: boolean
}

export interface ChatSession {
  id: number
  user_id: number
  title: string
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: number
  session_id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  sources?: string
  created_at: string
}

export interface Document {
  id: number
  user_id: number
  title: string
  file_name?: string
  file_size: number
  chunk_count: number
  status: string
  created_at: string
}

export interface StreamMeta {
  session_id: number
  session_title: string
}
