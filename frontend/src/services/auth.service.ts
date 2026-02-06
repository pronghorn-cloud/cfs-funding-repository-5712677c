import api from './api'
import type { TokenResponse, UserProfile } from '@/types'

const isDev = import.meta.env.DEV

export const authService = {
  async login(): Promise<TokenResponse | void> {
    if (isDev) {
      const { data } = await api.get<TokenResponse>('/auth/dev-login')
      return data
    }
    window.location.href = '/api/v1/auth/login'
  },

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return data
  },

  async logout(refreshToken: string): Promise<void> {
    await api.post('/auth/logout', { refresh_token: refreshToken })
  },

  async getProfile(): Promise<UserProfile> {
    const { data } = await api.get<UserProfile>('/auth/me')
    return data
  },
}
