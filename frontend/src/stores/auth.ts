import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/client'
import type { UserInfo } from '../types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(username: string, password: string) {
    const { data } = await authApi.login({ username, password })
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)
    userInfo.value = { id: data.user_id, username: data.username, nickname: data.username, is_superuser: false }
    return data
  }

  async function fetchUserInfo() {
    if (!token.value) return
    try {
      const { data } = await authApi.me()
      userInfo.value = data
    } catch {
      userInfo.value = null
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return { token, userInfo, isLoggedIn, login, fetchUserInfo, logout }
})
