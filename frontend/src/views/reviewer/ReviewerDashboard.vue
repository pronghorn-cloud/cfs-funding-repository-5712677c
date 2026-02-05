<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApplicationsStore } from '@/stores/applications'
import { useReviewsStore } from '@/stores/reviews'

const router = useRouter()
const appStore = useApplicationsStore()
const reviewStore = useReviewsStore()

onMounted(async () => {
  await Promise.all([
    appStore.fetchApplications({ status: 'under_review' }),
    reviewStore.fetchMyReviews(),
  ])
})
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold mb-6">Reviewer Dashboard</h1>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div class="bg-white rounded-lg shadow p-6 text-center">
        <div class="text-3xl font-bold text-goa-blue">
          {{ appStore.applications?.total ?? 0 }}
        </div>
        <div class="text-gray-600">Pending Reviews</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6 text-center">
        <div class="text-3xl font-bold text-goa-success">
          {{ reviewStore.myReviews.filter(r => r.status === 'completed').length }}
        </div>
        <div class="text-gray-600">Completed Reviews</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6 text-center">
        <div class="text-3xl font-bold text-goa-warning">
          {{ reviewStore.myReviews.filter(r => r.status === 'in_progress').length }}
        </div>
        <div class="text-gray-600">In Progress</div>
      </div>
    </div>

    <!-- Applications needing review -->
    <div class="bg-white rounded-lg shadow">
      <div class="flex justify-between items-center p-4 border-b">
        <h2 class="text-xl font-semibold">Applications for Review</h2>
        <goa-button type="secondary" size="compact" @_click="router.push('/reviews/compare')">
          Compare Applications
        </goa-button>
      </div>

      <goa-spinner v-if="appStore.isLoading" />

      <goa-table v-else class="w-full">
        <thead>
          <tr>
            <th>Application</th>
            <th>Type</th>
            <th>Amount</th>
            <th>Submitted</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="app in appStore.applications?.items" :key="app.id">
            <td>{{ app.title }}</td>
            <td>{{ app.funding_type }}</td>
            <td>{{ app.amount_requested ? `$${Number(app.amount_requested).toLocaleString()}` : '-' }}</td>
            <td>{{ app.submitted_at ? new Date(app.submitted_at).toLocaleDateString() : '-' }}</td>
            <td>
              <goa-button type="primary" size="compact" @_click="router.push(`/reviews/${app.id}`)">
                Review
              </goa-button>
            </td>
          </tr>
        </tbody>
      </goa-table>
    </div>
  </div>
</template>
