<script setup lang="ts">
import { useAuth } from '@/composables/useAuth'
import { useNotificationsStore } from '@/stores/notifications'
import { useRouter, useRoute } from 'vue-router'

const { user, logout } = useAuth()
const notifications = useNotificationsStore()
const router = useRouter()
const route = useRoute()

async function handleLogout() {
  await logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <goa-app-header heading="CFS Funding Portal - Administration" url="/">
      <nav class="flex items-center gap-4 text-sm" aria-label="Admin navigation">
        <router-link to="/dashboard" class="text-white hover:underline">Portal</router-link>
        <span class="text-white/70">{{ user?.display_name }}</span>
        <button @click="handleLogout" class="text-white hover:underline">Logout</button>
      </nav>
    </goa-app-header>

    <!-- Notifications -->
    <div class="fixed top-16 right-4 z-50 flex flex-col gap-2" aria-live="polite">
      <goa-notification
        v-for="n in notifications.notifications"
        :key="n.id"
        :type="n.type === 'success' ? 'event' : n.type === 'error' ? 'emergency' : 'information'"
        @_dismiss="notifications.removeNotification(n.id)"
      >
        {{ n.message }}
      </goa-notification>
    </div>

    <div class="flex flex-1">
      <!-- Side menu -->
      <aside class="w-64 bg-gray-50 border-r border-gray-200 p-4" role="navigation" aria-label="Admin sidebar">
        <goa-side-menu>
          <router-link to="/admin" custom v-slot="{ navigate, isExactActive }">
            <a @click="navigate" :class="{ 'font-bold text-goa-blue': isExactActive }" class="block py-2 px-3 rounded hover:bg-gray-100">
              Dashboard
            </a>
          </router-link>
          <router-link to="/admin/users" custom v-slot="{ navigate, isExactActive }">
            <a @click="navigate" :class="{ 'font-bold text-goa-blue': isExactActive }" class="block py-2 px-3 rounded hover:bg-gray-100">
              User Management
            </a>
          </router-link>
          <router-link to="/admin/config" custom v-slot="{ navigate, isExactActive }">
            <a @click="navigate" :class="{ 'font-bold text-goa-blue': isExactActive }" class="block py-2 px-3 rounded hover:bg-gray-100">
              System Config
            </a>
          </router-link>
          <hr class="my-3" />
          <router-link to="/vulnerability" class="block py-2 px-3 rounded hover:bg-gray-100">Vulnerability Index</router-link>
          <router-link to="/reports" class="block py-2 px-3 rounded hover:bg-gray-100">Reports</router-link>
          <router-link to="/reviews" class="block py-2 px-3 rounded hover:bg-gray-100">Reviews</router-link>
        </goa-side-menu>
      </aside>

      <main id="main-content" class="flex-1 p-6" role="main">
        <router-view />
      </main>
    </div>

    <goa-app-footer>
      <a href="https://www.alberta.ca/disclaimer" slot="meta">Disclaimer</a>
      <a href="https://www.alberta.ca/privacy" slot="meta">Privacy</a>
      <a href="https://www.alberta.ca/accessibility" slot="meta">Accessibility</a>
    </goa-app-footer>
  </div>
</template>
