import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/index.js'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null)
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  function setToken(newToken) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('access_token', newToken)
    } else {
      localStorage.removeItem('access_token')
    }
  }

  async function login(email, password) {
    loading.value = true
    error.value = null
    try {
      const res = await authApi.login(email, password)
      setToken(res.data.access_token)
      await fetchMe()
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed'
      return false
    } finally {
      loading.value = false
    }
  }

  async function register(email, password) {
    loading.value = true
    error.value = null
    try {
      const res = await authApi.register(email, password)
      setToken(res.data.access_token)
      await fetchMe()
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Registration failed'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    try {
      const res = await authApi.me()
      user.value = res.data
    } catch {
      user.value = null
    }
  }

  function logout() {
    setToken(null)
    user.value = null
  }

  return { token, user, loading, error, isAuthenticated, login, register, logout, fetchMe }
})
