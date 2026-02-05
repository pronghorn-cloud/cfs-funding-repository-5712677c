<script setup lang="ts">
import { onMounted } from 'vue'
import { useApplicationsStore } from '@/stores/applications'

const appStore = useApplicationsStore()

onMounted(async () => {
  await appStore.fetchApplications({ status: 'reviewed' })
})
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold mb-6">Compare Applications</h1>

    <goa-callout type="information" heading="Application Comparison">
      Compare reviewed applications side-by-side to inform funding decisions.
    </goa-callout>

    <goa-spinner v-if="appStore.isLoading" />

    <div v-else class="mt-6">
      <goa-table class="w-full">
        <thead>
          <tr>
            <th>Application</th>
            <th>Organization</th>
            <th>Type</th>
            <th>Amount Requested</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="app in appStore.applications?.items" :key="app.id">
            <td>{{ app.title }}</td>
            <td>{{ app.organization_id }}</td>
            <td>{{ app.funding_type }}</td>
            <td>{{ app.amount_requested ? `$${Number(app.amount_requested).toLocaleString()}` : '-' }}</td>
            <td><goa-badge :content="app.status" /></td>
          </tr>
        </tbody>
      </goa-table>
    </div>
  </div>
</template>
