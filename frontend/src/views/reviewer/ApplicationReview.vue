<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApplicationsStore } from '@/stores/applications'
import { reviewsService, type ReviewScoreInput } from '@/services/reviews.service'
import { useNotificationsStore } from '@/stores/notifications'

const route = useRoute()
const router = useRouter()
const appStore = useApplicationsStore()
const notifications = useNotificationsStore()

const appId = route.params.appId as string

const criteria = [
  { name: 'need_assessment', label: 'Need Assessment', weight: 0.2 },
  { name: 'project_viability', label: 'Project Viability', weight: 0.2 },
  { name: 'budget_appropriateness', label: 'Budget Appropriateness', weight: 0.15 },
  { name: 'organizational_capacity', label: 'Organizational Capacity', weight: 0.15 },
  { name: 'expected_outcomes', label: 'Expected Outcomes', weight: 0.15 },
  { name: 'community_impact', label: 'Community Impact', weight: 0.15 },
]

const scores = ref<Record<string, number>>({})
const comments = ref<Record<string, string>>({})
const recommendation = ref('')
const notes = ref('')

criteria.forEach((c) => {
  scores.value[c.name] = 0
  comments.value[c.name] = ''
})

const overallScore = computed(() => {
  let weighted = 0
  let totalWeight = 0
  for (const c of criteria) {
    if (scores.value[c.name] > 0) {
      weighted += scores.value[c.name] * c.weight
      totalWeight += c.weight
    }
  }
  return totalWeight > 0 ? (weighted / totalWeight).toFixed(1) : '0.0'
})

onMounted(async () => {
  await appStore.fetchApplication(appId)
})

async function submitReview() {
  const scoreInputs: ReviewScoreInput[] = criteria.map((c) => ({
    criteria: c.name,
    score: scores.value[c.name],
    weight: c.weight,
    comments: comments.value[c.name] || undefined,
  }))

  try {
    await reviewsService.create(appId, scoreInputs, recommendation.value, notes.value)
    notifications.success('Review submitted successfully')
    router.push('/reviews')
  } catch (e: any) {
    notifications.error(e.response?.data?.detail || 'Failed to submit review')
  }
}
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold mb-2">Application Review</h1>
    <p class="text-gray-600 mb-6" v-if="appStore.currentApplication">
      {{ appStore.currentApplication.title }}
    </p>

    <goa-spinner v-if="appStore.isLoading" />

    <template v-else>
      <!-- Application Summary -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-xl font-semibold mb-3">Application Summary</h2>
        <div class="grid grid-cols-2 gap-4" v-if="appStore.currentApplication">
          <div>
            <span class="text-sm text-gray-500">Funding Type</span>
            <p class="font-medium">{{ appStore.currentApplication.funding_type }}</p>
          </div>
          <div>
            <span class="text-sm text-gray-500">Amount Requested</span>
            <p class="font-medium">
              {{ appStore.currentApplication.amount_requested
                ? `$${Number(appStore.currentApplication.amount_requested).toLocaleString()}`
                : 'N/A' }}
            </p>
          </div>
        </div>
      </div>

      <!-- Scoring -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold">Scoring Criteria</h2>
          <div class="text-right">
            <span class="text-sm text-gray-500">Overall Score</span>
            <div class="text-2xl font-bold text-goa-blue">{{ overallScore }}</div>
          </div>
        </div>

        <div v-for="c in criteria" :key="c.name" class="border-b last:border-0 py-4">
          <div class="flex justify-between items-start mb-2">
            <div>
              <label class="font-medium">{{ c.label }}</label>
              <span class="text-sm text-gray-500 ml-2">(Weight: {{ (c.weight * 100).toFixed(0) }}%)</span>
            </div>
            <div class="text-xl font-bold" :class="scores[c.name] >= 7 ? 'text-goa-success' : scores[c.name] >= 4 ? 'text-goa-warning' : 'text-goa-emergency'">
              {{ scores[c.name] }}/10
            </div>
          </div>
          <input
            type="range"
            min="0"
            max="10"
            step="1"
            v-model.number="scores[c.name]"
            class="w-full"
            :aria-label="`Score for ${c.label}`"
          />
          <goa-form-item label="Comments" class="mt-2">
            <goa-textarea
              :name="`comment_${c.name}`"
              :value="comments[c.name]"
              @_change="(e: any) => comments[c.name] = e.detail.value"
              rows="2"
              placeholder="Optional comments..."
            />
          </goa-form-item>
        </div>
      </div>

      <!-- Recommendation -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Recommendation</h2>
        <goa-form-item label="Recommendation" requirement="required">
          <goa-dropdown
            name="recommendation"
            :value="recommendation"
            @_change="(e: any) => recommendation = e.detail.value"
          >
            <goa-dropdown-item value="approve" label="Recommend Approval" />
            <goa-dropdown-item value="deny" label="Recommend Denial" />
            <goa-dropdown-item value="request_info" label="Request Additional Information" />
          </goa-dropdown>
        </goa-form-item>
        <goa-form-item label="Notes" class="mt-4">
          <goa-textarea
            name="notes"
            :value="notes"
            @_change="(e: any) => notes = e.detail.value"
            rows="4"
            placeholder="Additional notes for the decision maker..."
          />
        </goa-form-item>
      </div>

      <div class="flex justify-end gap-3">
        <goa-button type="secondary" @_click="router.back()">Cancel</goa-button>
        <goa-button type="primary" @_click="submitReview">Submit Review</goa-button>
      </div>
    </template>
  </div>
</template>
