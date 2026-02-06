<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useApplicationsStore } from '@/stores/applications'

const { user } = useAuth()
const appStore = useApplicationsStore()
const router = useRouter()

onMounted(async () => {
  await appStore.fetchApplications({
    organization_id: user.value?.organization_id ?? undefined,
  })
})

function getStatusBadgeType(status: string): string {
  switch (status) {
    case 'draft': return 'midtone'
    case 'submitted': return 'information'
    case 'under_review': return 'information'
    case 'approved': return 'success'
    case 'denied': return 'emergency'
    default: return 'midtone'
  }
}
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">My Dashboard</h1>
      <goa-button type="primary" @_click="router.push('/applications/new')">
        New Application
      </goa-button>
    </div>

    <goa-callout type="information" heading="Welcome" v-if="user" class="mb-6">
      Hello, {{ user.display_name }}. You are logged in as <strong>{{ user.role }}</strong>.
    </goa-callout>

    <!-- Applications Table -->
    <div class="bg-white rounded-lg shadow">
      <h2 class="text-xl font-semibold p-4 border-b">My Applications</h2>

      <goa-spinner v-if="appStore.isLoading" />

      <div v-else-if="appStore.applications?.items.length === 0" class="p-8 text-center text-gray-500">
        No applications yet. Click "New Application" to get started.
      </div>

      <table v-else class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-3 font-semibold text-gray-700">Title</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-700">Type</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-700">Status</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-700">Amount</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-700">Submitted</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-700">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="app in appStore.applications?.items" :key="app.id" class="border-b border-gray-100 hover:bg-gray-50">
            <td class="px-4 py-3">{{ app.title }}</td>
            <td class="px-4 py-3">{{ app.funding_type }}</td>
            <td class="px-4 py-3">
              <goa-badge :type="getStatusBadgeType(app.status)" :content="app.status" />
            </td>
            <td class="px-4 py-3">{{ app.amount_requested ? `$${Number(app.amount_requested).toLocaleString('en-CA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '-' }}</td>
            <td class="px-4 py-3">{{ app.submitted_at ? new Date(app.submitted_at).toLocaleDateString() : '-' }}</td>
            <td class="px-4 py-3">
              <goa-button type="tertiary" size="compact" @_click="router.push(`/applications/${app.id}`)">
                View
              </goa-button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
