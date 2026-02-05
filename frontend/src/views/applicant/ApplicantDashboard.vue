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

      <goa-table v-else class="w-full">
        <thead>
          <tr>
            <th>Title</th>
            <th>Type</th>
            <th>Status</th>
            <th>Amount</th>
            <th>Submitted</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="app in appStore.applications?.items" :key="app.id">
            <td>{{ app.title }}</td>
            <td>{{ app.funding_type }}</td>
            <td>
              <goa-badge :type="getStatusBadgeType(app.status)" :content="app.status" />
            </td>
            <td>{{ app.amount_requested ? `$${Number(app.amount_requested).toLocaleString()}` : '-' }}</td>
            <td>{{ app.submitted_at ? new Date(app.submitted_at).toLocaleDateString() : '-' }}</td>
            <td>
              <goa-button type="tertiary" size="compact" @_click="router.push(`/applications/${app.id}`)">
                View
              </goa-button>
            </td>
          </tr>
        </tbody>
      </goa-table>
    </div>
  </div>
</template>
