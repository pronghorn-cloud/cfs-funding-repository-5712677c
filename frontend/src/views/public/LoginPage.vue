<script setup lang="ts">
import { useAuth } from '@/composables/useAuth'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { onMounted } from 'vue'

const { login, isAuthenticated } = useAuth()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

async function handleLogin() {
  await login()
  if (isAuthenticated.value) {
    const redirect = (route.query.redirect as string) || '/dashboard'
    router.replace(redirect)
  }
}

onMounted(() => {
  // Handle OAuth callback
  const accessToken = route.query.access_token as string
  const refreshToken = route.query.refresh_token as string

  if (accessToken && refreshToken) {
    authStore.handleCallback(accessToken, refreshToken)
    const redirect = (route.query.redirect as string) || '/dashboard'
    router.replace(redirect)
    return
  }

  if (isAuthenticated.value) {
    router.replace('/dashboard')
  }
})
</script>

<template>
  <div class="w-full max-w-md mx-auto">
    <div class="bg-white rounded-lg shadow-lg p-8">
      <h1 class="text-2xl font-bold text-center mb-2">Sign In</h1>
      <p class="text-gray-600 text-center mb-8">
        Access the CFS Funding Portal
      </p>

      <goa-button type="primary" size="compact" @_click="handleLogin()" class="w-full">
        Sign in with Alberta.ca Account
      </goa-button>

      <div class="mt-6 text-center text-sm text-gray-500">
        <p>You will be redirected to Microsoft Azure AD for authentication.</p>
      </div>
    </div>
  </div>
</template>
