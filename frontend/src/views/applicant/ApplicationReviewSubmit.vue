<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApplicationsStore } from '@/stores/applications'
import { useAuth } from '@/composables/useAuth'
import { useNotificationsStore } from '@/stores/notifications'

const router = useRouter()
const appStore = useApplicationsStore()
const { user } = useAuth()
const notifications = useNotificationsStore()

const draft = appStore.draftFormData

const fundingTypeLabels: Record<string, string> = {
  operational: 'Operational Funding',
  capital: 'Capital Funding',
  emergency: 'Emergency Funding',
  project_based: 'Project-Based Funding',
}

onMounted(() => {
  if (!draft) {
    router.replace({ name: 'application-new' })
  }
})

function editApplication() {
  router.push({ name: 'application-new' })
}

async function submitApplication() {
  if (!draft) return

  // Create the application in the database
  const app = await appStore.createApplication({
    organization_id: user.value?.organization_id ?? '',
    title: draft.title,
    funding_type: draft.funding_type,
    amount_requested: draft.amount_requested ?? undefined,
    fiscal_year: draft.fiscal_year,
    description: draft.description,
  })

  if (app) {
    // Save section data
    await appStore.saveSection(app.id, 'project_description', {
      project_goals: draft.project_goals,
      target_population: draft.target_population,
      timeline: draft.timeline,
    }, true)

    await appStore.saveSection(app.id, 'budget', {
      budget_breakdown: draft.budget_breakdown,
      other_funding: draft.other_funding,
    }, true)

    await appStore.saveSection(app.id, 'outcomes', {
      kpis: draft.kpis,
      expected_impact: draft.expected_impact,
    }, true)

    // Transition to submitted
    await appStore.submitApplication(app.id)

    if (!appStore.error) {
      appStore.draftFormData = null
      notifications.success('Application submitted successfully!')
      router.push('/dashboard')
    } else {
      notifications.error(appStore.error)
    }
  } else if (appStore.error) {
    notifications.error(appStore.error)
  }
}

function formatAmount(amount: number | null): string {
  if (amount === null) return 'Not specified'
  return `$${amount.toLocaleString('en-CA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}
</script>

<template>
  <div v-if="draft">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Review Your Application</h1>
      <goa-button type="secondary" @_click="editApplication">
        Edit Application
      </goa-button>
    </div>

    <goa-callout type="information" class="mb-6">
      Please review all the information below before submitting. Once submitted, your application will be sent for review and cannot be edited.
    </goa-callout>

    <!-- Section 1: Application Details -->
    <div class="bg-white rounded-lg shadow p-6 mb-4">
      <h2 class="text-xl font-semibold mb-4 text-goa-blue-700">Application Details</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
        <div>
          <p class="text-sm font-semibold text-gray-500">Application Title</p>
          <p class="mt-1">{{ draft.title }}</p>
        </div>
        <div>
          <p class="text-sm font-semibold text-gray-500">Funding Type</p>
          <p class="mt-1">{{ fundingTypeLabels[draft.funding_type] || draft.funding_type }}</p>
        </div>
        <div>
          <p class="text-sm font-semibold text-gray-500">Amount Requested (CAD)</p>
          <p class="mt-1">{{ formatAmount(draft.amount_requested) }}</p>
        </div>
        <div>
          <p class="text-sm font-semibold text-gray-500">Fiscal Year</p>
          <p class="mt-1">{{ draft.fiscal_year || 'Not specified' }}</p>
        </div>
      </div>
      <div class="mt-4" v-if="draft.description">
        <p class="text-sm font-semibold text-gray-500">Description</p>
        <p class="mt-1 whitespace-pre-wrap">{{ draft.description }}</p>
      </div>
    </div>

    <!-- Section 2: Project Description -->
    <div class="bg-white rounded-lg shadow p-6 mb-4">
      <h2 class="text-xl font-semibold mb-4 text-goa-blue-700">Project Description</h2>
      <div class="space-y-4">
        <div v-if="draft.project_goals">
          <p class="text-sm font-semibold text-gray-500">Project Goals</p>
          <p class="mt-1 whitespace-pre-wrap">{{ draft.project_goals }}</p>
        </div>
        <div v-if="draft.target_population">
          <p class="text-sm font-semibold text-gray-500">Target Population</p>
          <p class="mt-1 whitespace-pre-wrap">{{ draft.target_population }}</p>
        </div>
        <div v-if="draft.timeline">
          <p class="text-sm font-semibold text-gray-500">Implementation Timeline</p>
          <p class="mt-1 whitespace-pre-wrap">{{ draft.timeline }}</p>
        </div>
        <p v-if="!draft.project_goals && !draft.target_population && !draft.timeline" class="text-gray-400 italic">No project description provided.</p>
      </div>
    </div>

    <!-- Section 3: Budget -->
    <div class="bg-white rounded-lg shadow p-6 mb-4">
      <h2 class="text-xl font-semibold mb-4 text-goa-blue-700">Budget Details</h2>
      <div class="space-y-4">
        <div v-if="draft.budget_breakdown">
          <p class="text-sm font-semibold text-gray-500">Budget Breakdown</p>
          <p class="mt-1 whitespace-pre-wrap">{{ draft.budget_breakdown }}</p>
        </div>
        <div v-if="draft.other_funding">
          <p class="text-sm font-semibold text-gray-500">Other Funding Sources</p>
          <p class="mt-1 whitespace-pre-wrap">{{ draft.other_funding }}</p>
        </div>
        <p v-if="!draft.budget_breakdown && !draft.other_funding" class="text-gray-400 italic">No budget details provided.</p>
      </div>
    </div>

    <!-- Section 4: Outcomes -->
    <div class="bg-white rounded-lg shadow p-6 mb-4">
      <h2 class="text-xl font-semibold mb-4 text-goa-blue-700">Expected Outcomes</h2>
      <div class="space-y-4">
        <div v-if="draft.kpis">
          <p class="text-sm font-semibold text-gray-500">Key Performance Indicators</p>
          <p class="mt-1 whitespace-pre-wrap">{{ draft.kpis }}</p>
        </div>
        <div v-if="draft.expected_impact">
          <p class="text-sm font-semibold text-gray-500">Expected Impact</p>
          <p class="mt-1 whitespace-pre-wrap">{{ draft.expected_impact }}</p>
        </div>
        <p v-if="!draft.kpis && !draft.expected_impact" class="text-gray-400 italic">No outcomes provided.</p>
      </div>
    </div>

    <!-- Section 5: Documents -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4 text-goa-blue-700">Supporting Documents</h2>
      <div v-if="draft.uploadedFileNames.length > 0" class="space-y-2">
        <div
          v-for="(fileName, index) in draft.uploadedFileNames"
          :key="index"
          class="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded px-4 py-2 text-sm"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>{{ fileName }}</span>
        </div>
      </div>
      <p v-else class="text-gray-400 italic">No documents uploaded.</p>
    </div>

    <!-- Submit -->
    <div class="flex justify-between items-center">
      <goa-button type="secondary" @_click="editApplication">
        Edit Application
      </goa-button>
      <goa-button type="primary" @_click="submitApplication">
        Submit Application
      </goa-button>
    </div>
  </div>
</template>
