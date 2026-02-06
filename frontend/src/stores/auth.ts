import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/auth.service'
import type { UserProfile } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const user = ref<UserProfile | null>(null)
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!accessToken.value)
  const userRole = computed(() => user.value?.role ?? null)
  const isAdmin = computed(() => userRole.value === 'admin')
  const isReviewer = computed(() => userRole.value === 'reviewer' || userRole.value === 'admin')

  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  async function fetchProfile() {
    if (!accessToken.value) return
    try {
      isLoading.value = true
      user.value = await authService.getProfile()
    } catch {
      user.value = null
    } finally {
      isLoading.value = false
    }
  }

  async function refreshTokens() {
    if (!refreshToken.value) throw new Error('No refresh token')
    const response = await authService.refreshToken(refreshToken.value)
    setTokens(response.access_token, response.refresh_token)
  }

  async function logout() {
    if (refreshToken.value) {
      try {
        await authService.logout(refreshToken.value)
      } catch {
        // Ignore logout errors
      }
    }
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function login() {
    const result = await authService.login()
    if (result) {
      setTokens(result.access_token, result.refresh_token)
      await fetchProfile()
    }
  }

  // Handle callback tokens from URL params
  function handleCallback(access: string, refresh: string) {
    setTokens(access, refresh)
    fetchProfile()
  }

  return {
    accessToken,
    refreshToken,
    user,
    isLoading,
    isAuthenticated,
    userRole,
    isAdmin,
    isReviewer,
    setTokens,
    fetchProfile,
    refreshTokens,
    logout,
    login,
    handleCallback,
  }
})
