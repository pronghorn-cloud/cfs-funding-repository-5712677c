<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useApplicationsStore } from '@/stores/applications'

const appStore = useApplicationsStore()

const stats = ref({
  totalApplications: 0,
  pendingReviews: 0,
  approved: 0,
  totalFunding: 0,
})

onMounted(async () => {
  await appStore.fetchApplications({ page_size: 100 })
  if (appStore.applications) {
    stats.value.totalApplications = appStore.applications.total
    stats.value.pendingReviews = appStore.applications.items.filter(
      (a) => a.status === 'under_review' || a.status === 'submitted',
    ).length
    stats.value.approved = appStore.applications.items.filter(
      (a) => a.status === 'approved',
    ).length
  }
})
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold mb-6">Administration Dashboard</h1>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white rounded-lg shadow p-6 text-center">
        <div class="text-3xl font-bold text-goa-blue">{{ stats.totalApplications }}</div>
        <div class="text-gray-600">Total Applications</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6 text-center">
        <div class="text-3xl font-bold text-goa-warning">{{ stats.pendingReviews }}</div>
        <div class="text-gray-600">Pending Reviews</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6 text-center">
        <div class="text-3xl font-bold text-goa-success">{{ stats.approved }}</div>
        <div class="text-gray-600">Approved</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6 text-center">
        <div class="text-3xl font-bold text-goa-blue">${{ stats.totalFunding.toLocaleString() }}</div>
        <div class="text-gray-600">Total Funding</div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Quick Actions</h2>
        <div class="space-y-3">
          <router-link to="/reviews" class="block p-3 border rounded hover:bg-gray-50">
            Review pending applications
          </router-link>
          <router-link to="/vulnerability" class="block p-3 border rounded hover:bg-gray-50">
            View Vulnerability Index
          </router-link>
          <router-link to="/reports" class="block p-3 border rounded hover:bg-gray-50">
            Generate reports
          </router-link>
          <router-link to="/admin/users" class="block p-3 border rounded hover:bg-gray-50">
            Manage users
          </router-link>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Recent Activity</h2>
        <p class="text-gray-500">Activity feed will appear here once applications are being processed.</p>
      </div>
    </div>
  </div>
</template>
