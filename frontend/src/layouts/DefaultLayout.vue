<script setup lang="ts">
import { useAuth } from '@/composables/useAuth'
import { useNotificationsStore } from '@/stores/notifications'
import { useRouter } from 'vue-router'

const { user, isAuthenticated, logout } = useAuth()
const notifications = useNotificationsStore()
const router = useRouter()

async function handleLogout() {
  await logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <goa-app-header
      heading="CFS Funding Portal"
      url="/"
    >
      <template v-if="isAuthenticated">
        <nav class="flex items-center gap-4 text-sm" aria-label="Main navigation">
          <router-link to="/dashboard" class="text-white hover:underline">Dashboard</router-link>
          <router-link to="/reviews" class="text-white hover:underline" v-if="user?.role === 'reviewer' || user?.role === 'admin'">Reviews</router-link>
          <router-link to="/vulnerability" class="text-white hover:underline" v-if="user?.role === 'reviewer' || user?.role === 'admin'">Vulnerability</router-link>
          <router-link to="/reports" class="text-white hover:underline" v-if="user?.role === 'admin'">Reports</router-link>
          <router-link to="/admin" class="text-white hover:underline" v-if="user?.role === 'admin'">Admin</router-link>
          <span class="text-white/70">{{ user?.display_name }}</span>
          <button @click="handleLogout" class="text-white hover:underline">Logout</button>
        </nav>
      </template>
    </goa-app-header>

    <!-- Notifications -->
    <div class="fixed top-16 right-4 z-50 flex flex-col gap-2" aria-live="polite">
      <goa-notification
        v-for="n in notifications.notifications"
        :key="n.id"
        :type="n.type === 'success' ? 'event' : n.type === 'error' ? 'emergency' : n.type === 'warning' ? 'important' : 'information'"
        @_dismiss="notifications.removeNotification(n.id)"
      >
        {{ n.message }}
      </goa-notification>
    </div>

    <main id="main-content" class="flex-1 max-w-7xl mx-auto w-full py-6" role="main" style="padding-left: 18px; padding-right: 18px;">
      <router-view />
    </main>

    <footer class="border-t border-gray-200 bg-gray-50 py-4">
      <div class="text-center">
        <nav class="flex justify-center gap-[2em] text-sm" aria-label="Footer links">
          <a href="https://www.alberta.ca/disclaimer" class="text-goa-blue hover:underline">Disclaimer</a>
          <a href="https://www.alberta.ca/privacy" class="text-goa-blue hover:underline">Privacy</a>
          <a href="https://www.alberta.ca/accessibility" class="text-goa-blue hover:underline">Accessibility</a>
        </nav>
        <p class="text-xs text-gray-500 mt-2">&copy; {{ new Date().getFullYear() }} Government of Alberta</p>
      </div>
    </footer>
  </div>
</template>
