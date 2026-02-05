import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useAuth() {
  const store = useAuthStore()

  return {
    user: computed(() => store.user),
    isAuthenticated: computed(() => store.isAuthenticated),
    isAdmin: computed(() => store.isAdmin),
    isReviewer: computed(() => store.isReviewer),
    role: computed(() => store.userRole),
    login: () => store.login(),
    logout: () => store.logout(),
    fetchProfile: () => store.fetchProfile(),
  }
}
